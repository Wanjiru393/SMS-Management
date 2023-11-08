from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.contrib.auth import login
from .forms import CustomerInformationForm, MessageTemplateForm, TemplateSubmissionForm, UserRegistrationForm
from django.contrib.auth.decorators import permission_required, login_required
from .models import TemplateSubmission, Approval, CustomerInformation, Message, TemplateSubmission


def assign_approval_role(request, user_id, approval_permission):
    user = User.objects.get(pk=user_id)

    if approval_permission == 'can_approve':
        group = Group.objects.get(name='Can Approve')
        permission = Permission.objects.get(codename='can_approve_template')
    elif approval_permission == 'cannot_approve':
        group = Group.objects.get(name='Cannot Approve')
        permission = Permission.objects.get(codename='cannot_approve_template')
    else:
        return HttpResponse("Invalid permission assignment.")

    user.groups.add(group)
    user.user_permissions.add(permission)

    messages.success(request, f"Role and permission assigned to {user.username} successfully.")
    return redirect('admin-user-list')

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def create_customer_information(request):
    if request.method == 'POST':
        form = CustomerInformationForm(request.POST)
        if form.is_valid():
            customer_information = form.save()
            return redirect('create_message_template', customer_information_id=customer_information.id)
    else:
        form = CustomerInformationForm()
    
    return render(request, 'create_customer_information.html', {'form': form})

@login_required
def create_message_template(request, customer_information_id):
    customer_information = CustomerInformation.objects.get(pk=customer_information_id)
    
    if request.method == 'POST':
        form = MessageTemplateForm(request.POST)
        if form.is_valid():
            message_template = form.save()
            template_submission = TemplateSubmission.objects.create(template=message_template, user=request.user)
            return redirect('submit_message_for_approval', template_submission_id=template_submission.id)
    else:
        form = MessageTemplateForm()
    
    return render(request, 'create_message_template.html', {'form': form, 'customer_information': customer_information})

@login_required
def submit_message_for_approval(request, template_submission_id):
    try:
        template_submission = TemplateSubmission.objects.get(pk=template_submission_id)
    except TemplateSubmission.DoesNotExist:
        return HttpResponse("Template submission not found.")
    
    if request.method == 'POST':
        # Handle form submission for message approval
        form = TemplateSubmissionForm(request.POST, instance=template_submission)
        if form.is_valid():
            form.save()
            # Notify admin or designated users for approval
            messages.success(request, "Message submitted for approval.")
            return redirect('message_list')
    else:
        form = TemplateSubmissionForm(instance=template_submission)
    
    return render(request, 'submit_message_for_approval.html', {'form': form, 'template_submission': template_submission})

@permission_required('can_approve_template', raise_exception=True)
def approve_message(request, template_submission_id):
    try:
        template_submission = TemplateSubmission.objects.get(pk=template_submission_id)
    except TemplateSubmission.DoesNotExist:
        return HttpResponse("Template submission not found.")
    
    if request.method == 'POST':
        template_submission.approved = True
        template_submission.save()
        
        # Create an approval record
        Approval.objects.create(submission=template_submission, approver=request.user)
        
        messages.success(request, "Template submission approved successfully.")
        return redirect('message_list')

    return render(request, 'approve_message.html', {'template_submission': template_submission})

@login_required
def message_list(request):
    # List messages that have been approved
    approved_messages = Message.objects.filter(approved=True)
    return render(request, 'message_list.html', {'approved_messages': approved_messages})
