from django.contrib import admin

# Register your models here.
from Grades.models import *


class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ['person', 'module', 'mc_assistant']


admin.site.register(Coordinator, CoordinatorAdmin)


class GradeAdmin(admin.ModelAdmin):
    list_display = ('test_id', 'time', 'student_id', 'grade')
    list_filter = ['test_id', 'time', 'student_id', 'grade']


admin.site.register(Grade, GradeAdmin)


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('person', 'course', 'role')
    list_filter = ['person', 'course', 'role']


admin.site.register(Teacher, TeacherAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_id', 'start', 'stop', 'user')
    list_filter = ['id_prefix']


admin.site.register(Person, PersonAdmin)


for object in [Study, Studying, Module, Module_ed, Criterion, Course, Test]:
    admin.site.register(object)
