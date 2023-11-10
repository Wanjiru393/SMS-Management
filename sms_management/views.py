from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import permission_required, login_required
from .models import MessageTemplate, TemplateSubmission, CustomerInformation, Message, TemplateSubmission, BulkSMS, Approval, UserProfile
from .forms import CustomerInformationForm, MessageTemplateForm, TemplateSubmissionForm, UserRegistrationForm
from django.shortcuts import get_object_or_404


def assign_approval_role(request, user_id, approval_permission):
    user = User.objects.get(pk=user_id)

    if approval_permission == 'can_approve':
        group = Group.objects.get(name='Can Approve')
    elif approval_permission == 'cannot_approve':
        group = Group.objects.get(name='Cannot Approve')
    else:
        return HttpResponse("Invalid permission assignment.")

    user.groups.add(group)

    messages.success(request, f"Role assigned to {user.username} successfully.")
    return redirect('admin-user-list')

from django.contrib.auth.models import User

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please choose a different username.")
                return redirect('register_user')
            user = form.save()

            # Create a UserProfile 
            UserProfile.objects.get_or_create(user=user, full_name=form.cleaned_data['full_name'],
                                              staff_number=form.cleaned_data['staff_number'],
                                              department=form.cleaned_data['department'],
                                              station=form.cleaned_data['station'])

            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request=request, template_name="auth/login.html", context={"login_form": form})


def dashboard(request):
    pending_count = TemplateSubmission.objects.filter(status='pending').count()
    approved_count = TemplateSubmission.objects.filter(status='approved').count()

    # Get message templates
    message_templates = MessageTemplate.objects.all()

    # Get message history
    message_history = BulkSMS.objects.all()

    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'message_templates': message_templates,
        'message_history': message_history,
    }

    return render(request, 'dashboard.html', context)


@login_required
def create_customer_information(request):
    if request.method == 'POST':
        form = CustomerInformationForm(request.POST)
        if form.is_valid():
            customer_information = form.save()
            return redirect('create_message_template', customer_information_id=customer_information.id)
    else:
        form = CustomerInformationForm()
    
    return render(request, 'customer_infor.html', {'form': form})

@login_required
def create_message_template(request, customer_information_id):
    customer_information = CustomerInformation.objects.get(pk=customer_information_id)
    
    if request.method == 'POST':
        form = MessageTemplateForm(request.POST)
        if form.is_valid():
            message_template = form.save()
            template_submission = TemplateSubmission(template=message_template, user=request.user)
            template_submission.save()
            return redirect('submit_message_for_approval', template_submission_id=template_submission.id)
    else:
        form = MessageTemplateForm()
    
    return render(request, 'message_template.html', {'form': form, 'customer_information': customer_information})

@login_required
def submit_message_for_approval(request, template_submission_id):
    try:
        template_submission = TemplateSubmission.objects.get(pk=template_submission_id)
    except TemplateSubmission.DoesNotExist:
        return HttpResponse("Template submission not found.")
    
    if request.method == 'POST':
        form = TemplateSubmissionForm(request.POST, instance=template_submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Message submitted for approval.")
            return redirect('message_list')
    else:
        form = TemplateSubmissionForm(instance=template_submission)
    
    return render(request, 'approval.html', {'form': form, 'template_submission': template_submission})

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
