from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.contrib.auth import login
from .  import UserRegistrationForm  
from django.contrib.auth.decorators import permission_required
from .models import TemplateSubmission, Approval


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


@permission_required('can_approve_template', raise_exception=True)
def approve_message(request, template_submission_id):
    try:
        template_submission = TemplateSubmission.objects.get(pk=template_submission_id)
    except TemplateSubmission.DoesNotExist:
        return HttpResponse("Template submission not found.")
    if request.user.has_perm('your_app_name.can_approve_template'):
        template_submission.approved = True
        template_submission.save()

        # Create an approval record
        Approval.objects.create(submission=template_submission, approver=request.user)

        messages.success(request, "Template submission approved successfully.")
    else:
        return HttpResponse("You do not have permission to approve template submissions.")

    return redirect('message_list') 