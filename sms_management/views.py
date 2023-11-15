import csv
import datetime
import io
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, Group
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


def home (request):
    pending_count = TemplateSubmission.objects.filter(status='pending').count()
    approved_count = TemplateSubmission.objects.filter(status='approved').count()

    message_history = BulkSMS.objects.all()

    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'message_history': message_history,
    }

    return render(request, 'home.html', context)


@login_required
def  create_customer_information(request):
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
    message_content = ''
    bulk_sms = None
    

    if not available_templates:
        messages.error(request, "No templates available.")
        return redirect('create_customer_information')

    if request.method == 'POST':
        form = TemplateSubmissionForm(request.POST)
        if form.is_valid():
            template_submission = form.save(commit=False)
            template_submission.user = request.user
            template_submission.status = 'pending' 
            template_submission.save()

            message_content = template_submission.template.content.format(
                customer_name=customer.full_name,
                amount="...",
                payment_method="...",
                account_number=customer.acc_number
            )

            bulk_sms = BulkSMS.objects.create(
                messages=message_content,
                mobile=customer.contact,
                create_date=datetime.now(),
                user_id=request.user.username,
            )

            Message.objects.create(
                sender=request.user,
                recipient=customer,
                content=message_content,
                submission=template_submission,
                bulk_sms=bulk_sms,
                issue_type=template_submission.template.issue_type,
            )

            return redirect('customer_infor', customer_id=customer_id)
        else:
            print("Form errors:", form.errors) 
            messages.error(request, "Invalid form data.")
    else:
        form = TemplateSubmissionForm()

    return render(request, 'create_message.html', {
        'customer': customer,
        'form': form,
        'available_templates': available_templates,
        'message_content': message_content,
        'bulk_sms': bulk_sms,
    })


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
