from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import generic, View
from django.utils import timezone
from django.db.models import Q
import django_excel as excel
from xlsxwriter.utility import xl_rowcol_to_cell

import re

from Grades.exceptions import GradeException
from Grades.models import ModuleEdition, Grade, Test, Person, ModulePart, Studying, Module, Study
from importer.forms import GradeUploadForm, TestGradeUploadForm, ImportStudentForm, ImportStudentModule


# Create your views here.


class MCImporterIndexView(LoginRequiredMixin, View):
    model = ModuleEdition

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        if ModuleEdition.objects.filter(coordinators__user=self.request.user):
            return render(request, 'importer/mcindex.html', {
                'module_ed_list': ModuleEdition.objects.filter(coordinator__person__user=self.request.user).order_by(
                    'start')})
        elif ModulePart.objects.filter(teacher__person__user=self.request.user):
            return render(request, 'importer/teacherindex.html',
                          {'course_list': ModulePart.objects.filter(teacher__person__user=self.request.user).order_by(
                              'module_ed__start')})

        return HttpResponseForbidden('Only module coordinators can view this page.')

    def get_queryset(self):
        return ModuleEdition.objects.filter(coordinators__person__user=self.request.user).order_by('start')


COLUMN_TITLE_ROW = 5  # title-row, zero-indexed, that contains the title for the grade sheet rows.


@login_required
def import_module(request, pk):
    if not ModuleEdition.objects.filter(pk=pk):
        return HttpResponseNotFound('Module does not exist.')
    if not ModuleEdition.objects.filter(pk=pk).filter(coordinator__person__user=request.user):
        return HttpResponseForbidden('You are not the module coordinator for this course')

    if request.method == "POST":
        form = GradeUploadForm(request.POST, request.FILES)
        print('valid form')
        if form.is_valid():
            sheet = request.FILES['file'].get_book_dict()
            for table in sheet:

                test_rows = dict()

                student_id_field = None

                for title_index in range(0, len(sheet[table][COLUMN_TITLE_ROW])):
                    if sheet[table][COLUMN_TITLE_ROW][title_index] == '':
                        continue
                    if str(sheet[table][COLUMN_TITLE_ROW][title_index]).lower() == 'student_id':
                        student_id_field = title_index
                    else:
                        if Test.objects.filter(  # search by ID
                                pk=sheet[table][COLUMN_TITLE_ROW][title_index]
                        ).filter(module_part__module_edition=pk):
                            test_rows[title_index] = sheet[table][COLUMN_TITLE_ROW][title_index]
                        elif Test.objects.filter(  # search by name
                                name=sheet[table][COLUMN_TITLE_ROW][title_index]
                        ).filter(module_part__module_edition=pk):
                            test_rows[title_index] = Test.objects.filter(
                                name=sheet[table][COLUMN_TITLE_ROW][title_index]
                            ).filter(module_part__module_edition=pk)[0].pk
                        else:
                            pass  # Attempt to ignore test altogether.
                            # return HttpResponseBadRequest(
                            #     'Attempt to register grade for, amongst possible other tests, test: {} (interpreted from sheet coordinates {}), which is not part of this module. (Are you sure this test ID is correct and therefore part of your module?)'.format(
                            #         sheet[table][COLUMN_TITLE_ROW][title_index], xl_rowcol_to_cell(COLUMN_TITLE_ROW, title_index)))
                if student_id_field is None:
                    return HttpResponseBadRequest('excel file misses required header: \"student_id\"')

                teacher = Person.objects.get(user=request.user)

                grades = []

                tests = dict()
                for test_column in test_rows.keys():
                    tests[test_column] = Test.objects.get(pk=sheet[table][COLUMN_TITLE_ROW][test_column])

                # check for invalid students
                invalid_students = []
                for row in sheet[table][(COLUMN_TITLE_ROW + 1):]:
                    if not Studying.objects.filter(person__university_number=row[student_id_field]).filter(module_edition=pk):
                        invalid_students.append(row[student_id_field])
                if invalid_students:
                    return HttpResponseBadRequest(
                        'Students {} are not enrolled in this module. '
                        'Enroll these students first before retrying.'.format(invalid_students))

                for row in sheet[table][(COLUMN_TITLE_ROW + 1):]:
                    student = Person.objects.filter(university_number=row[student_id_field])[0]
                    if student:
                        for test_column in test_rows.keys():
                            try:
                                grades.append(make_grade(
                                    student=student,
                                    corrector=teacher,
                                    test=tests[test_column],
                                    grade=row[test_column]
                                ))
                            except GradeException as e:
                                return HttpResponseBadRequest(e)
                save_grades(grades)
            return redirect('grades:gradebook', pk)
        else:
            return HttpResponseBadRequest('Invalid file')
    else:
        if ModuleEdition.objects.filter(pk=pk):
            form = GradeUploadForm()
            return render(request, 'importer/importmodule.html', {'form': form, 'pk': pk})

        else:
            return HttpResponseBadRequest('This module does not exist.')


@login_required
def import_test(request, pk):
    if not Test.objects.filter(pk=pk):
        return HttpResponseNotFound('Test does not exist.')
    if not Test.objects.filter(
                    Q(module_part__teachers__user=request.user) |
                    Q(module_part__module_edition__coordinator__person__user=request.user)
    ).filter(pk=pk):
        return HttpResponseForbidden('Not allowed to alter test')

    if request.method == "POST":
        form = TestGradeUploadForm(request.POST, request.FILES)

        if form.is_valid():

            sheet = request.FILES['file'].get_book_dict()
            for table in sheet:
                try:
                    student_id_field = sheet[table][COLUMN_TITLE_ROW].index('student_id')
                    grade_field = sheet[table][COLUMN_TITLE_ROW].index('grade')
                    description_field = sheet[table][COLUMN_TITLE_ROW].index('description')
                except ValueError:
                    return HttpResponseBadRequest()

                teacher = Person.objects.get(user=request.user)

                invalid_students = []
                for row in sheet[table][(COLUMN_TITLE_ROW + 1):]:
                    if not Studying.objects.filter(module_id__courses__test__exact=pk, student_id__person_id=row[student_id_field]):
                        if not row[student_id_field] == '':
                            invalid_students.append(row[student_id_field])
                if invalid_students:
                    return HttpResponseBadRequest(
                        'Students {} are not enrolled in this module. '
                        'Enroll these students first before retrying.'.format(invalid_students))

                grades = []
                for row in sheet[table][(COLUMN_TITLE_ROW + 1):]:
                    try:
                        # Fix for empty student id field.
                        if not Person.objects.get(person_id=row[student_id_field]):
                            continue
                        grades.append(make_grade(
                            student=Person.objects.get(person_id=row[student_id_field]),
                            corrector=teacher,
                            test=Test.objects.get(pk=pk),
                            grade=row[grade_field],
                            description=row[description_field]
                        ))
                    except GradeException as e:
                        return HttpResponseBadRequest(e)
                save_grades(grades)
            return redirect('grades:test', pk)
        else:
            return HttpResponseBadRequest('Bad POST')
    else:
        if Test.objects.filter(pk=pk):
            form = TestGradeUploadForm()
            return render(request, 'importer/importtest.html',
                          {'test': Test.objects.get(pk=pk), 'form': form, 'pk': pk})

        else:
            return HttpResponseBadRequest('Test does not exist')


@login_required()
def export_module(request, pk):
    if not ModuleEdition.objects.filter(pk=pk).filter(coordinator__person__user=request.user):
        return HttpResponseForbidden('You are not the module coordinator for this course.')

    module = ModuleEdition.objects.get(pk=pk)
    students = Person.objects.filter(studying__module_edition=module)
    tests = Test.objects.filter(module_part__module_edition=module)

    table = [['' for _ in range(len(tests) + 1)] for _ in range(COLUMN_TITLE_ROW - 2)]

    if COLUMN_TITLE_ROW > 1:
        table.append(['Module part >'] + [test.module_part.name for test in tests])

    if COLUMN_TITLE_ROW > 0:
        table.append(['Test name >'] + [test.name for test in tests])

    table.append(['student_id'] + [test.pk for test in tests])

    for student in students:
        table.append([student.university_number] + [None for _ in range(len(tests))])

    return excel.make_response_from_array(table, 'xlsx')


@login_required()
def export_test(request, pk):
    if not Test.objects.filter(
                    Q(module_part__teachers__user=request.user) |
                    Q(module_part__module_edition__coordinator__person__user=request.user)
    ).filter(pk=pk):
        return HttpResponseForbidden('Not allowed to export test.')
    test = Test.objects.get(pk=pk)
    students = Person.objects.filter(studying__module_edition__modulepart=test.module_part)

    table = [['', '', ''] for _ in range(COLUMN_TITLE_ROW)]

    table.append(['student_id', 'grade', 'description'])

    for student in students:
        table.append([student.university_number, '', ''])

    return excel.make_response_from_array(table, 'xlsx')


def make_grade(student: Person, corrector: Person, test: Test, grade: float, description: str = ''):
    if grade == '':
        return  # Field is empty, assume it does not need to be imported.

    try:
        float(grade)
    except ValueError:
        raise GradeException('\'{}\' is not a valid input for a grade (found at {}\'s grade for {}.)'
                             .format(grade, student, test))  # Probably a typo, give an error.
    if test.minimum_grade > grade or grade > test.maximum_grade:
        raise GradeException(
            'Cannot register {}\'s ({}) grade for test {} because it\'s grade ({}) is outside the defined bounds '
            '({}-{}).'.format(student.name, student.univserity_number, test.name, grade, test.minimum_grade,
                              test.maximum_grade))

    try:
        grade_obj = Grade(
            student=student,
            teacher=corrector,
            test=test,
            grade=grade,
            time=timezone.now(),
            description=description
        )
    except Exception as e:
        raise GradeException(e)
    return grade_obj


def save_grades(grades):
    try:
        Grade.objects.bulk_create([grade for grade in grades if grade is not None])
    except Exception as e:
        raise GradeException('Error when saving grades to te database.')


@login_required
def import_student(request):
    if not ModuleEdition.objects.filter(Q(coordinator__person__user=request.user)):
        return HttpResponseForbidden('Not allowed to add students if not a module coordinator')

    if request.method == "POST":
        student_form = ImportStudentForm(request.POST, request.FILES)

        if student_form.is_valid():
            file = request.FILES['file']
            dict = file.get_book_dict()
            new_students = dict[list(dict.keys())[0]]
            string = ""
            if new_students[0][0].lower() == 'name' and new_students[0][1].lower() == 's-number' and new_students[0][
                2].lower() == 'starting date (dd/mm/yy)':
                for i in range(1, len(new_students)):
                    new_student = Person(name=new_students[i][0], university_number=new_students[i][1],
                                         start=new_students[i][2])
                    new_student.save()
                    string += "Student added:<br>"
                    string += "Name: %s<br>Number: %d<br>Start:%s<br>" % (
                        new_students[i][0], new_students[i][1], new_students[i][2])
                    string += "-----------------------------------------<br>"
                return HttpResponse(string)
            else:
                return HttpResponseBadRequest("Incorrect xls-format")


        else:
            return HttpResponseBadRequest('Bad POST')
    else:
        # if Module_ed.objects.filter(pk=pk):
        student_form = ImportStudentForm()
        return render(request, 'importer/import-new-student.html',
                      {'form': student_form})

        # else:
        # return HttpResponseBadRequest('You are not an Admin')


@login_required
def import_student_to_module(request, pk):
    if not ModuleEdition.objects.filter(  # ToDo: Check if User is actually Admin
            Q(coordinator__person__user=request.user)
    ).filter(pk=pk):
        return HttpResponseForbidden('Not allowed to upload students to module.')

    if request.method == "POST":
        student_form = ImportStudentForm(request.POST, request.FILES)
        print('hello')
        if student_form.is_valid():
            file = request.FILES['file']
            dict = file.get_book_dict()
            students_to_module = dict[list(dict.keys())[0]]
            string = ""
            startpattern = re.compile('start*')
            if students_to_module[0][0].lower() == 's-number' and students_to_module[0][1].lower() == 'name' and \
                    startpattern.match(students_to_module[0][
                                           2].lower()) and students_to_module[0][3].lower() == 'study' and \
                            students_to_module[0][4].lower() == 'role':
                context = {}
                context['created'] = []
                context['studying'] = []
                context['failed'] = []

                for i in range(1, len(students_to_module)):
                    student, created = Person.objects.get_or_create(
                        university_number=str(students_to_module[i][0]),
                        defaults={
                            'name': students_to_module[i][1],
                            'start': students_to_module[i][2],
                        }
                    )
                    if created:
                        context['created'].append([student.name, student.full_id])
                    studying, created = Studying.objects.get_or_create(
                        person=student,
                        module_edition=ModuleEdition.objects.get(pk=pk),
                        study=Study.objects.get(abbreviation=students_to_module[i][3]),
                        defaults={
                            'role': students_to_module[i][4],
                        }
                    )
                    if created:
                        module_ed = ModuleEdition.objects.get(id=studying.module_edition.pk)
                        module = Module.objects.get(moduleedition=module_ed)
                        context['studying'].append(
                            [student.name, student.full_id, module.name, module_ed.code, studying.study])
                    else:
                        module_ed = ModuleEdition.objects.get(id=studying.module_edition.pk)
                        module = Module.objects.get(moduleedition=module_ed)
                        context['failed'].append(
                            [student.name, student.full_id, module.name, module_ed.code, studying.study])
                        context['studying'].append(
                            [student.name, student.full_id, module.name, module_ed.code, studying.study])
                print(context)
                return render(request, 'importer/students-module-imported.html', context={'context': context})
            else:
                return HttpResponseBadRequest("Incorrect xls-format")
        else:
            return HttpResponseBadRequest('Bad POST')

    else:  # if Module_ed.objects.filter(pk=pk):
        student_form = ImportStudentModule()
        return render(request, 'importer/import-module-student.html',
                      {'form': student_form, 'pk': pk})

# else:
# return HttpResponseBadRequest('You are not an Admin')
