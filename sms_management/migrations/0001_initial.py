# Generated by Django 4.2.7 on 2023-11-21 09:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('contact', models.CharField(max_length=15, unique=True)),
                ('acc_number', models.CharField(max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edited_template', models.TextField(blank=True, null=True)),
                ('issue', models.CharField(blank=True, max_length=200, null=True)),
                ('submission_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sms_management.customerinformation')),
            ],
            options={
                'permissions': [('can_approve_message', 'Can Approve message Submissions'), ('cannot_approve_message', 'Cannot Approve message Submissions')],
            },
        ),
        migrations.CreateModel(
            name='MessageTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('issue_type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('staff_number', models.CharField(max_length=20)),
                ('department', models.CharField(max_length=100)),
                ('station', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SentMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('issue_type', models.CharField(max_length=100)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sms_management.customerinformation')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sms_management.messagesubmission')),
            ],
        ),
        migrations.AddField(
            model_name='messagesubmission',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sms_management.messagetemplate'),
        ),
        migrations.AddField(
            model_name='messagesubmission',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='BulkSMS',
            fields=[
                ('sms_id', models.AutoField(primary_key=True, serialize=False)),
                ('messages', models.TextField()),
                ('mobile', models.CharField(max_length=20)),
                ('create_date', models.DateTimeField()),
                ('date_sent', models.DateTimeField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sms_management.messagesubmission')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'INCMS_INTER_ADMINIS.BULK_SMS',
            },
        ),
        migrations.CreateModel(
            name='Approval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_date', models.DateTimeField(auto_now_add=True)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sms_management.messagesubmission')),
            ],
        ),
    ]
