from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register_user, name='register_user'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('send-sms/', views.send_sms_view, name='send_sms'),
    path('home/', views.home, name='home'),
    
    path('create-customer-information/', views.create_customer_information, name='create_customer_information'),
    path('create-message-template/', views.create_message_template, name='create_message_template'),
    path('edit-template/<int:template_id>/', views.edit_template, name='edit_template'),
    path('delete-template/<int:template_id>/', views.delete_template, name='delete_template'),

    path('create-message/<int:customer_id>/', views.create_message, name='create_message'),
    path('all_submissions/', views.all_submissions, name='all_submissions'),
    path('approve-submission/<int:submission_id>/', views.approve_submission, name='approve_submission'),
    path('edit-submission/<int:submission_id>/', views.edit_submission, name='edit_submission'),
    path('delete-submission/<int:submission_id>/', views.delete_submission, name='delete_submission'),

   
    path('assign_approval_role/<int:user_id>/<str:approval_permission>/', views.assign_approval_role, name='assign_approval_role'),
]
