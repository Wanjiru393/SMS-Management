from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views

urlpatterns = [
  path('', views.register_user, name='register_user'),
     path('login/', views.login_view, name='login'),
     path('dashboard/', views.dashboard, name='dashboard'),
    path('assign_approval_role/<int:user_id>/<str:approval_permission>/', views.assign_approval_role, name='assign_approval_role'),
    path('create-customer-information/', views.create_customer_information, name='create_customer_information'),
    path('create-message-template/<int:customer_information_id>/', views.create_message_template, name='create_message_template'),
    path('submit-message-for-approval/<int:template_submission_id>/', views.submit_message_for_approval, name='submit_message_for_approval'),
    path('approve-message/<int:template_submission_id>/', views.approve_message, name='approve_message'),
    path('message-list/', views.message_list, name='message_list'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    # path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
