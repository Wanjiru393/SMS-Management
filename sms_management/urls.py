from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_user, name='register_user'),
    path('assign_approval_role/<int:user_id>/<str:approval_permission>/', views.assign_approval_role, name='assign_approval_role'),
    path('create_customer_information/', views.create_customer_information, name='create_customer_information'),
    path('create_message_template/<int:customer_information_id>/', views.create_message_template, name='create_message_template'),
    path('submit_message_for_approval/<int:template_submission_id>/', views.submit_message_for_approval, name='submit_message_for_approval'),
    path('approve_message/<int:template_submission_id>/', views.approve_message, name='approve_message'),
    path('message_list/', views.message_list, name='message_list'),
]
