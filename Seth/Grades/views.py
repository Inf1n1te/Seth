from collections import OrderedDict
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views import generic
from .models import Studying, Person, ModuleEdition, Test, ModulePart, Grade
import csv
import re
from django.utils.encoding import smart_str


class ModuleView(generic.ListView):
    template_name = 'Grades/modules.html'
    context_object_name = 'module_list'

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not ModuleEdition.objects.filter(Q(coordinators__user=user) | Q(modulepart__teachers__user=user)):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        module_set = ModuleEdition.objects.filter(Q(coordinators__user=user) | Q(modulepart__teachers__user=user))
        return set(module_set)


class GradeView(generic.DetailView):
    template_name = 'Grades/gradebook2.html'
    model = ModuleEdition

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not ModuleEdition.objects.filter(Q(coordinators__user=user) | Q(modulepart__teachers__user=user),
                                            id=self.kwargs['pk']):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GradeView, self).get_context_data(**kwargs)

        mod_ed = ModuleEdition.objects.prefetch_related('studying_set').get(id=self.kwargs['pk'])

        dicts = Studying.objects \
            .prefetch_related('person', 'study', 'person__Submitter') \
            .values('study__name', 'study__abbreviation', 'person', 'person__name', 'person__university_number',
                    'person__Submitter', 'person__Submitter__grade', 'person__Submitter__test',
                    'person__Submitter__released') \
            .filter(module_edition=mod_ed) \
            .order_by('person__Submitter__test', 'person__Submitter__time')
        module_parts = ModulePart.objects \
            .filter(Q(module_edition__coordinators__user=self.request.user) | Q(teachers__user=self.request.user),
                    Q(module_edition=mod_ed)) \
            .order_by('id').distinct()

        tests = Test.objects \
            .filter(Q(module_part__module_edition__coordinators__user=self.request.user) | Q(
            module_part__teachers__user=self.request.user), Q(module_part__module_edition=mod_ed)) \
            .order_by('module_part__id').distinct()

        students = dict()
        temp_dict = dict()
        testallreleased = dict()
        grade_dict = OrderedDict()

        for d in dicts:
            student = d['person']
            if student not in students.keys():
                students[student] = dict()
            if student not in temp_dict.keys():
                temp_dict[student] = dict()

            students[student]['name'] = d['person__name']
            students[student]['pid'] = d['person__university_number']
            students[student]['study'] = d['study__name']
            students[student]['sstudy'] = d['study__abbreviation']

            temp_dict[student][d['person__Submitter__test']] = (
                d['person__Submitter__grade'], d['person__Submitter__released'])

            if not d['person__Submitter__test'] in testallreleased.keys():
                testallreleased[d['person__Submitter__test']] = True
            if not d['person__Submitter__released']:
                testallreleased[d['person__Submitter__test']] = False

        for key in sorted(temp_dict):
            grade_dict[key] = temp_dict[key]

        context['gradedict'] = grade_dict
        context['studentdict'] = students
        context['module_parts'] = module_parts
        context['testallreleased'] = testallreleased
        context['tests'] = tests

        return context


class StudentView(generic.DetailView):
    template_name = 'Grades/student.html'
    model = Person

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not Studying.objects.filter(person__user=user, person__id=self.kwargs['pk']):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StudentView, self).get_context_data(**kwargs)

        person = Person.objects.get(id=self.kwargs['pk'])

        module_parts_dict = dict()
        test_dict = dict()

        dicts = Grade.objects \
            .prefetch_related('test') \
            .values('grade', 'released', 'test') \
            .filter(student=person, released=True) \
            .order_by('test', 'time')
        modules = ModuleEdition.objects \
            .filter(studying__person=person)

        for module_edition in modules:
            module_parts = ModulePart.objects \
                .filter(module_edition=module_edition, test__grade__released=True, test__grade__student=person) \
                .order_by('id').distinct('id')
            tests = Test.objects \
                .filter(module_part__module_edition=module_edition, grade__released=True, grade__student=person) \
                .order_by('module_part__id')

            module_parts_dict[module_edition] = module_parts
            test_dict[module_edition] = tests

        print(module_parts_dict)

        temp_dict = dict()
        context_dict = OrderedDict()

        for d in dicts:
            temp_dict[d['test']] = d['grade']

        for key in sorted(temp_dict):
            context_dict[key] = temp_dict[key]

        context['student'] = person
        context['modules'] = modules
        context['module_parts'] = module_parts_dict
        context['tests'] = test_dict
        context['gradedict'] = context_dict

        return context


class ModuleStudentView(generic.DetailView):
    template_name = 'Grades/modulestudent.html'
    model = ModuleEdition

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not ModuleEdition.objects.filter(Q(coordinators__user=user) | Q(modulepart__teachers__user=user),
                                            id=self.kwargs['pk']):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ModuleStudentView, self).get_context_data(**kwargs)

        mod_ed = ModuleEdition.objects.get(id=self.kwargs['pk'])
        student = Person.objects.get(id=self.kwargs['sid'])

        dicts = Grade.objects \
            .prefetch_related('test') \
            .values('grade', 'released', 'test') \
            .filter(test__module_part__module_edition=mod_ed, student=student) \
            .order_by('test', 'time')
        module_parts = ModulePart.objects \
            .prefetch_related('test_set') \
            .filter(Q(module_edition__coordinators__user=self.request.user) | Q(teachers__user=self.request.user),
                    Q(module_edition=mod_ed)) \
            .order_by('id').distinct()
        tests = Test.objects \
            .filter(Q(module_part__module_edition__coordinators__user=self.request.user) | Q(
            module_part__teachers__user=self.request.user), Q(module_part__module_edition=mod_ed)) \
            .order_by('module_part__id').distinct()

        temp_dict = dict()
        context_dict = OrderedDict()

        for d in dicts:
            temp_dict[d['test']] = (d['grade'], d['released'])

        for key in sorted(temp_dict):
            context_dict[key] = temp_dict[key]

        context['student'] = student
        context['module_parts'] = module_parts
        context['tests'] = tests
        context['gradedict'] = context_dict

        return context


class ModulePartView(generic.DetailView):
    template_name = 'Grades/module_part.html'
    model = ModulePart

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not ModulePart.objects.filter(Q(module_edition__coordinators__user=user) | Q(teachers__user=user),
                                         id=self.kwargs['pk']):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ModulePartView, self).get_context_data(**kwargs)

        module_part = ModulePart.objects.get(id=self.kwargs['pk'])

        dicts = Studying.objects \
            .prefetch_related('person', 'study', 'person__Submitter') \
            .values('study__name', 'study__abbreviation', 'person', 'person__name', 'person__university_number',
                    'person__Submitter', 'person__Submitter__grade', 'person__Submitter__test',
                    'person__Submitter__released') \
            .filter(module_edition__modulepart=module_part) \
            .order_by('person__Submitter__test', 'person__Submitter__time')
        tests = Test.objects \
            .filter(module_part=module_part)

        students = dict()
        temp_dict = dict()
        testallreleased = dict()
        grade_dict = OrderedDict()

        for d in dicts:
            student = d['person']
            if student not in students.keys():
                students[student] = dict()
            if student not in temp_dict.keys():
                temp_dict[student] = dict()

            students[student]['name'] = d['person__name']
            students[student]['pid'] = d['person__university_number']
            students[student]['study'] = d['study__name']
            students[student]['sstudy'] = d['study__abbreviation']

            temp_dict[student][d['person__Submitter__test']] = (
                d['person__Submitter__grade'], d['person__Submitter__released'])

            if not d['person__Submitter__test'] in testallreleased.keys():
                testallreleased[d['person__Submitter__test']] = True
            if not d['person__Submitter__released']:
                testallreleased[d['person__Submitter__test']] = False

        for key in sorted(temp_dict):
            grade_dict[key] = temp_dict[key]

        context['gradedict'] = grade_dict
        context['studentdict'] = students
        context['module_part'] = module_part
        context['testallreleased'] = testallreleased
        context['tests'] = tests
        return context


class TestView(generic.DetailView):
    template_name = 'Grades/test.html'
    model = Test

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not Test.objects.filter(
                        Q(module_part__module_edition__coordinators__user=user) | Q(module_part__teachers__user=user),
                id=self.kwargs['pk']):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)

        if 'change' not in self.request.session.keys():
            context['change'] = False
        elif self.request.session['change'] == 1:
            context['change'] = 'The chosen grade(s) have successfully been released.'
        elif self.request.session['change'] == 2:
            context['change'] = 'The chosen grade(s) have successfully been retracted.'
        self.request.session['change'] = 0

        test = Test.objects.get(id=self.kwargs['pk'])

        dicts = Studying.objects \
            .prefetch_related('person', 'study', 'person__Submitter') \
            .values('study__name', 'study__abbreviation', 'person', 'person__name', 'person__university_number',
                    'person__Submitter', 'person__Submitter__grade', 'person__Submitter__test',
                    'person__Submitter__released') \
            .filter(module_edition__modulepart__test=test) \
            .order_by('person__Submitter__test', 'person__Submitter__time')

        students = dict()
        temp_dict = dict()
        testallreleased = dict()
        grade_dict = OrderedDict()

        for d in dicts:
            student = d['person']
            if student not in students.keys():
                students[student] = dict()
            if student not in temp_dict.keys():
                temp_dict[student] = dict()

            students[student]['name'] = d['person__name']
            students[student]['pid'] = d['person__university_number']
            students[student]['study'] = d['study__name']
            students[student]['sstudy'] = d['study__abbreviation']

            temp_dict[student][d['person__Submitter__test']] = (
                d['person__Submitter__grade'], d['person__Submitter__released'])

            if not d['person__Submitter__test'] in testallreleased.keys():
                testallreleased[d['person__Submitter__test']] = True
            if not d['person__Submitter__released']:
                testallreleased[d['person__Submitter__test']] = False

        for key in sorted(temp_dict):
            grade_dict[key] = temp_dict[key]

        context['gradedict'] = grade_dict
        context['studentdict'] = students
        context['testallreleased'] = testallreleased
        context['test'] = test
        return context


def export(request, *args, **kwargs):
    user = request.user

    if not ModuleEdition.objects.filter(coordinators__user=user, id=kwargs['pk']):
        raise PermissionDenied()

    mod_ed = ModuleEdition.objects.prefetch_related('studying_set').prefetch_related('module_parts').get(
        id=kwargs['pk'])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + mod_ed.module.name + '.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    output = u'Student'
    for module_part in mod_ed.module_parts.prefetch_related('test_set').all():
        for test in module_part.test_set.all():
            output += ',' + test.name

    writer.writerow([
        smart_str(output),
    ])

    for studying in mod_ed.studying_set.prefetch_related('student'):

        output = u'' + studying.student.user.last_name + ' (' + studying.student.univserity_number + ')'
        for module_part in mod_ed.module_parts.prefetch_related('test_set').all():
            for test in module_part.test_set.prefetch_related('grade_set').all():

                gradelist = []
                for grade in test.grade_set.filter(student=studying.student):
                    gradelist.append(grade)

                gradelist.sort(key=lambda gr: grade.time)
                if gradelist != []:
                    output += ',' + str(gradelist[-1].grade)
                else:
                    output += ',-'
        writer.writerow([
            smart_str(output)
        ])
    return response


def release(request, *args, **kwargs):
    user = request.user

    if not ModuleEdition.objects.filter(coordinators__user=user, id=kwargs['pk']):
        raise PermissionDenied()

    action = request.POST['action']

    for key in request.POST:
        key_search = re.search('check([0-9]+)', key)
        if key_search:
            grade_id = int(key_search.group(1))
            grade = Grade.objects.get(id=grade_id)

            if action == 'release':
                grade.released = True
                grade.save()
                request.session['change'] = 1
            elif action == 'retract':
                grade.released = False
                grade.save()
                request.session['change'] = 2

    # TODO: Send mail

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
