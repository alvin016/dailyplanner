from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('autosave/', views.autosave, name='autosave'),
    path('autosave_reflection/', views.autosave_reflection, name='autosave_reflection'),
    path('edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('toggle_task_completed/', views.toggle_task_completed, name='toggle_task_completed'),

]