# Generated migration for DoctorProfile model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('doctors', '0001_initial'),  # Adjust based on your last migration
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorProfile',
            fields=[
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True,
                    related_name='doctor_profile',
                    serialize=False,
                    to=settings.AUTH_USER_MODEL
                )),
                ('license_number', models.CharField(
                    blank=True,
                    null=True,
                    max_length=50,
                    help_text='Professional license number (PRC)',
                    unique=True
                )),
                ('specialization', models.CharField(
                    choices=[
                        ('general_medicine', 'General Medicine'),
                        ('general_dentistry', 'General Dentistry'),
                        ('pediatrics', 'Pediatrics'),
                        ('internal_medicine', 'Internal Medicine'),
                        ('orthopedics', 'Orthopedics'),
                        ('dermatology', 'Dermatology'),
                        ('ophthalmology', 'Ophthalmology'),
                        ('ent', 'ENT (Ear, Nose, Throat)'),
                        ('orthodontics', 'Orthodontics'),
                        ('oral_surgery', 'Oral Surgery'),
                        ('other', 'Other'),
                    ],
                    default='general_medicine',
                    help_text='Medical/dental specialization',
                    max_length=50
                )),
                ('department', models.CharField(
                    default='Medical Services',
                    help_text='Department or clinic',
                    max_length=100
                )),
                ('years_of_experience', models.PositiveIntegerField(
                    default=0,
                    help_text='Years of professional experience'
                )),
                ('qualifications', models.TextField(
                    blank=True,
                    help_text='Educational background and certifications',
                    null=True
                )),
                ('office_location', models.CharField(
                    blank=True,
                    help_text='Office or clinic location',
                    max_length=200,
                    null=True
                )),
                ('consultation_hours', models.TextField(
                    blank=True,
                    help_text='Available consultation hours',
                    null=True
                )),
                ('signature_image', models.ImageField(
                    blank=True,
                    help_text='Digital signature for certificates',
                    null=True,
                    upload_to='signatures/'
                )),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Whether doctor is currently active'
                )),
                ('is_available_for_appointments', models.BooleanField(
                    default=True,
                    help_text='Whether doctor accepts new appointments'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'doctor profile',
                'verbose_name_plural': 'doctor profiles',
                'ordering': ['user__last_name', 'user__first_name'],
            },
        ),
        migrations.AddIndex(
            model_name='doctorprofile',
            index=models.Index(fields=['license_number'], name='doctors_doc_license_idx'),
        ),
        migrations.AddIndex(
            model_name='doctorprofile',
            index=models.Index(fields=['specialization'], name='doctors_doc_special_idx'),
        ),
        migrations.AddIndex(
            model_name='doctorprofile',
            index=models.Index(fields=['is_active'], name='doctors_doc_is_acti_idx'),
        ),
    ]