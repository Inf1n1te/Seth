from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'module_management'
urlpatterns = [
    url(r'^$', login_required(views.IndexView.as_view()), name='module_overview'),
    url(r'^(?P<pk>.+)/module_detail$', login_required(views.ModuleView.as_view()), name='module_detail'),
    url(r'^(?P<pk>.+)/module_ed_detail$', login_required(views.ModuleEdView.as_view()), name='module_ed_detail'),
    url(r'^(?P<pk>.+)/course_detail$', login_required(views.CourseView.as_view()), name='course_detail'),
    url(r'^(?P<pk>.+)/test_detail$', login_required(views.TestView.as_view()), name='test_detail'),
    url(r'^(?P<pk>.+)/module_ed_update$', login_required(views.ModuleEdUpdateView.as_view()), name='module_ed_update'),
    url(r'^(?P<pk>.+)/course_update$', login_required(views.CourseUpdateView.as_view()), name='course_update'),
    url(r'^(?P<pk>.+)/test_update$', login_required(views.TestUpdateView.as_view()), name='test_update'),
    url(r'^(?P<pk>.+)/module_ed_create$', login_required(views.ModuleEdCreateView.as_view()), name='module_ed_create'),
    url(r'^(?P<pk>.+)/course_create$', login_required(views.CourseCreateView.as_view()), name='course_create'),
    url(r'^(?P<pk>.+)/test_create$', login_required(views.TestCreateView.as_view()), name='test_create'),
    url(r'^(?P<pk>.+)/course_delete$', login_required(views.CourseDeleteView.as_view()), name='course_delete'),
    url(r'^(?P<pk>.+)/test_delete$', login_required(views.TestDeleteView.as_view()), name='test_delete')
]
