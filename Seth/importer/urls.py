from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'importer'
urlpatterns = [
    url(r'^$', views.ImporterIndexView.as_view(), name='index'),
    url(r'module/(?P<pk>[0-9]+)/get_workbook$', views.export_module, name='export_module'),
    url(r'test/(?P<pk>[0-9]+)/get_workbook$', views.export_test, name='export_test'),
    url(r'module_part/(?P<pk>[0-9]+)/get_workbook$', views.export_module_part, name='export_module_part'),
    url(r'module_part/(?P<pk>[0-9]+)/get_signoff_workbook$', views.export_module_part_signoff, name='export_module_part_signoff'),
    url(r'import_module/(?P<pk>[0-9]+)$', views.ImportModuleView.as_view(), name='import_module'),
    url(r'module_part/(?P<pk>[0-9]+)$', views.import_module_part, name='import_module_part'),
    url(r'test/(?P<pk>[0-9]+)$', views.import_test, name='import_test'),
    url(r'import-module-student/(?P<pk>[0-9]+)$', views.import_student_to_module, name='import_student_to_module'),
    url(r'import-module-student/(?P<pk>[0-9]+)/get_workbook$', views.workbook_student_to_module, name='export_student_to_module'),
    url(r'import-module-structure/(?P<pk>[0-9]+)/get_workbook$', views.export_module_structure, name='export_module_structure'),
    url(r'import-module-structure/(?P<pk>[0-9]+)$', views.ModuleStructureImporter.as_view(), name='import_module_structure'),

    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
