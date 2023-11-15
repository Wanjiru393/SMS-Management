from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_user, name='register_user'),
    path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('create-customer-information/', views.create_customer_information, name='create_customer_information'),

    path('create-message-template/', views.create_message_template, name='create_message_template'),
    path('edit-template/<int:template_id>/', views.edit_template, name='edit_template'),
    path('delete-template/<int:template_id>/', views.delete_template, name='delete_template'),

    path('create-message/<int:customer_id>/', views.create_message, name='create_message'),
    path('submit-message-for-approval/<int:template_submission_id>/', views.submit_message_for_approval, name='submit_message_for_approval'),
    path('approve-message/<int:template_submission_id>/', views.approve_message, name='approve_message'),
    path('message-list/', views.message_list, name='message_list'),
    path('assign_approval_role/<int:user_id>/<str:approval_permission>/', views.assign_approval_role, name='assign_approval_role'),
]
