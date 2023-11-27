import io
import csv
from django.contrib.auth import logout
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import permission_required, login_required
from .models import CustomerInformation, MessageTemplate, MessageSubmission, BulkSMS, UserProfile, Approval, User, SentMessage
from .forms import MessageSubmissionForm, UserRegistrationForm, CustomerInformationForm, MessageTemplateForm


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


def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            staff_number = form.cleaned_data['staff_number']
            print(f"Attempting to register user with staff_number: {staff_number}")

            if User.objects.filter(username=staff_number).exists():
                messages.error(request, "Staff number already exists. Please choose a different staff number.")
                return redirect('register_user')

            user = form.save(commit=True)
            user_profile = UserProfile.objects.get(user=user)
            user_profile.full_name = form.cleaned_data['full_name']
            user_profile.staff_number = staff_number
            user_profile.department = form.cleaned_data['department']
            user_profile.station = form.cleaned_data['station']
            user_profile.save()

            backend = 'sms_management.backends.StaffNumberBackend'
            user.backend = backend
            login(request, user)

            messages.success(request, f"Registration successful. You are now logged in as {staff_number}.")
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            staff_number = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, staff_number=staff_number, password=password, backend='sms_management.backends.StaffNumberBackend')

            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {staff_number}.")
                return redirect('home')
            else:
                messages.error(request, "Invalid staff_number or password.")
        else:
            messages.error(request, "Invalid staff_number or password.")
    else:
        form = AuthenticationForm()

    return render(request=request, template_name="auth/login.html", context={"login_form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')


def home(request):
    pending_count = MessageSubmission.objects.filter(status='pending').count()
    approved_count = MessageSubmission.objects.filter(status='approved').count()

    # Get all approved messages by submission date(latest first)
    approved_messages = MessageSubmission.objects.filter(status='approved').order_by('-submission_date')
        
    message_history = SentMessage.objects.all()

    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'approved_messages': approved_messages,
        'message_history': message_history,
    }

    return render(request, 'home.html', context)


@login_required
def create_customer_information(request):
    records = CustomerInformation.objects.all()
    
    if request.method == 'POST':
        form = CustomerInformationForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "This is not a csv file")
            else:
                data_set = csv_file.read().decode('UTF-8')
                io_string = io.StringIO(data_set)
                next(io_string)
                for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                    _, created = CustomerInformation.objects.update_or_create(
                        full_name=column[0],
                        contact=column[1],
                        acc_number=column[2],
                    )
                records = CustomerInformation.objects.all()
                
                messages.success(request, "Data population successful.")
                return render(request, 'customer_infor.html', {'form': form, 'records': records})
    else:
        form = CustomerInformationForm()

    return render(request, 'customer_infor.html', {'form': form, 'records': records})


@login_required
def create_message_template(request):
    templates = MessageTemplate.objects.all()
    if request.method == 'POST':
        form = MessageTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            templates = MessageTemplate.objects.all()
            messages.success(request, "Template created successfully.")
    else:
        form = MessageTemplateForm()

    return render(request, 'create_template.html', {'form': form, 'templates': templates})

@login_required
def edit_template(request, template_id):
    template = get_object_or_404(MessageTemplate, pk=template_id)
    if request.method == 'POST':
        form = MessageTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, "Template updated successfully.")
            return redirect('create_message_template')
    else:
        form = MessageTemplateForm(instance=template)

    return render(request, 'create_template.html', {'form': form})

@login_required
def delete_template(request, template_id):
    template = get_object_or_404(MessageTemplate, pk=template_id)
    if request.method == 'POST':
        template.delete()
        messages.success(request, "Template deleted successfully.")
        return redirect('create_message_template')

    return render(request, 'create_template.html', {'template': template})

@login_required
def create_message(request, customer_id):
    customer = get_object_or_404(CustomerInformation, pk=customer_id)
    available_templates = MessageTemplate.objects.all()
    
    if request.method == 'POST':
        template_id = request.POST.get('template')
        if not template_id:
            return HttpResponse("No template ID provided.")
        template = get_object_or_404(MessageTemplate, pk=template_id)
        issue = request.POST.get('issue')
        edited_template = request.POST.get('message_content')

        # Create MessageSubmission instance
        submission, created = MessageSubmission.objects.get_or_create(
            template=template, user=request.user,customer=customer, edited_template=edited_template, defaults={'status': 'pending'})
        
        if created:
            messages.success(request, 'Message created successfully.')
            return redirect('all_submissions')

    return render(request, 'create_message.html', {'customer': customer, 'available_templates': available_templates})

@login_required
def edit_submission(request, submission_id):
    submission = get_object_or_404(MessageSubmission, pk=submission_id)
    
    if request.method == 'POST':
        form = MessageSubmissionForm(request.POST, instance=submission, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Submission updated successfully.")
            return redirect('all_submissions')
        else:
            messages.error(request, "There was an error in the form.")
    else:
        form = MessageSubmissionForm(instance=submission, user=request.user)

    return render(request, 'edit_submission.html', {'form': form})


@login_required
def delete_submission(request, submission_id):
    submission = get_object_or_404(MessageSubmission, pk=submission_id)
    if request.method == 'POST':
        submission.delete()
        messages.success(request, "Submission deleted successfully.")
        return redirect('all_submissions')
    return render(request, 'all_submissions.html', {'submission': submission})


@login_required
def all_submissions(request):
    messages = MessageSubmission.objects.all()
    return render(request, 'all_submissions.html', {'messages': messages})

@login_required
@permission_required('can_approve_message', raise_exception=True)
def approve_submission(request, submission_id):
    submission = get_object_or_404(MessageSubmission, pk=submission_id)
    approver = request.user

    # Create a new BulkSMS instance
    bulk_sms = BulkSMS(
        messages=submission.template.content,
        mobile=submission.customer.contact,
        user_id=approver,
        description=submission.issue,
        create_date=timezone.now(),
        submission=submission,
    )
    bulk_sms.save()

    # Create a new Approval instance
    approval = Approval(
        submission=submission,
        approver=approver,
        approval_date=timezone.now()
    )
    approval.save()

    # Update the status of the submission
    submission.status = 'approved'
    submission.save()
    return redirect('home')