from django import forms

from Grades.models import Person, Teacher, ModulePart


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', "university_number", 'email', 'start', "end", ]


class CreateUserForm(forms.Form):
    teacher_role_choices = ['---------', 'Teacher', 'Teaching Assistant']
    name = forms.CharField(label='Name', max_length=255)
    university_number = forms.CharField(label='University number', max_length=16)
    email_address = forms.EmailField(label='Email address')
    user = forms.ModelChoiceField(queryset=Person.objects.all())
    start_date = forms.DateField()
    end_date = forms.DateField()
    create_teacher = forms.BooleanField(required=False)
    role = forms.ChoiceField(choices=Teacher.ROLES)
    module_part = forms.ModelChoiceField(queryset=ModulePart.objects.all())
