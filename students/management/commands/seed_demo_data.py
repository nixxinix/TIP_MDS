"""
Management command to seed demo data for TIP MDS EMR.
Creates sample users, students, doctors, records, and appointments.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from students.models import StudentProfile, MedicalRecord
from doctors.models import DoctorProfile
from appointments.models import Appointment
from templates_docs.models import Template, IssuedCertificate

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with demo data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING('✓ Data cleared'))
        
        self.stdout.write('Seeding demo data...')
        
        # Create doctors
        doctors = self.create_doctors()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(doctors)} doctors'))
        
        # Create students
        students = self.create_students()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(students)} students'))
        
        # Create medical records
        records_count = self.create_medical_records(students, doctors)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {records_count} medical records'))
        
        # Create appointments
        appointments_count = self.create_appointments(students, doctors)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {appointments_count} appointments'))
        
        # Create templates
        templates_count = self.create_templates()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {templates_count} templates'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeding completed!'))
        self.stdout.write('\n📝 Login Credentials:')
        self.stdout.write('   Doctor: doctor@tip.edu.ph / password123')
        self.stdout.write('   Student: student1@tip.edu.ph / password123')
    
    def create_doctors(self):
        doctors = []
        doctor_data = [
            {
                'email': 'doctor@tip.edu.ph',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'license': 'PRC-123456',
                'specialization': 'general_medicine'
            },
            {
                'email': 'dentist@tip.edu.ph',
                'first_name': 'Carlos',
                'last_name': 'Reyes',
                'license': 'PRC-234567',
                'specialization': 'general_dentistry'
            },
            {
                'email': 'admin@tip.edu.ph',
                'first_name': 'Admin',
                'last_name': 'User',
                'license': 'PRC-345678',
                'specialization': 'general_medicine'
            },
        ]
        
        for data in doctor_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'doctor' if 'admin' not in data['email'] else 'admin',
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            profile, _ = DoctorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'license_number': data['license'],
                    'specialization': data['specialization'],
                    'department': 'Medical Services',
                    'years_of_experience': random.randint(5, 20),
                    'is_active': True,
                    'is_available_for_appointments': True,
                }
            )
            
            doctors.append(user)
        
        return doctors
    
    def create_students(self):
        students = []
        programs = ['CS', 'IT', 'CE', 'EE', 'ME']
        year_levels = ['1', '2', '3', '4']
        
        for i in range(1, 31):  # Create 30 students
            email = f'student{i}@tip.edu.ph'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': f'Student{i}',
                    'last_name': f'LastName{i}',
                    'role': 'student',
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'student_id': f'231034{i:02d}',
                    'program': random.choice(programs),
                    'year_level': random.choice(year_levels),
                    'sex': random.choice(['M', 'F']),
                    'date_of_birth': timezone.now().date() - timedelta(days=random.randint(6570, 9125)),
                    'contact_number': f'+63 912 345 {random.randint(1000, 9999)}',
                    'address': f'{random.randint(1, 999)} Sample St, Quezon City',
                    'emergency_contact_name': f'Parent {i}',
                    'emergency_contact_relationship': 'Parent',
                    'emergency_contact_number': f'+63 917 123 {random.randint(1000, 9999)}',
                    'height_cm': random.uniform(150, 190),
                    'weight_kg': random.uniform(45, 90),
                    'blood_type': random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                    'is_complete': True,
                    'is_verified': True,
                }
            )
            
            students.append(profile)
        
        return students
    
    def create_medical_records(self, students, doctors):
        diagnoses_medical = [
            'Upper Respiratory Tract Infection',
            'Headache/Migraine',
            'Gastritis',
            'Skin Allergies',
            'Fever',
            'Hypertension',
            'Common Cold',
            'Abdominal Pain',
        ]
        
        diagnoses_dental = [
            'Dental Caries',
            'Gingivitis',
            'Tooth Extraction',
            'Teeth Cleaning',
            'Tooth Filling',
            'Orthodontic Consultation',
        ]
        
        count = 0
        for student in students[:20]:  # First 20 students get records
            # Create 2-5 medical records per student
            num_records = random.randint(2, 5)
            for _ in range(num_records):
                record_type = random.choice(['medical', 'dental'])
                diagnoses = diagnoses_medical if record_type == 'medical' else diagnoses_dental
                
                MedicalRecord.objects.create(
                    student=student,
                    doctor=random.choice(doctors),
                    record_type=record_type,
                    visit_date=timezone.now().date() - timedelta(days=random.randint(1, 365)),
                    chief_complaint=f'Patient complains of {random.choice(["pain", "discomfort", "symptoms"])}',
                    diagnosis=random.choice(diagnoses),
                    procedure='Standard examination and treatment',
                    prescription='As prescribed by doctor',
                    remarks='Follow-up after 1 week',
                    status='approved',
                    approved_by=random.choice(doctors),
                    approved_at=timezone.now(),
                    blood_pressure=f'{random.randint(110, 140)}/{random.randint(70, 90)}' if record_type == 'medical' else None,
                    temperature=random.uniform(36.0, 37.5) if record_type == 'medical' else None,
                )
                count += 1
        
        return count
    
    def create_appointments(self, students, doctors):
        services = [
            'medical_consultation',
            'dental_cleaning',
            'dental_filling',
            'medical_clearance',
            'physical_exam',
        ]
        
        statuses = ['pending', 'approved', 'completed']
        
        count = 0
        for student in students[:15]:  # First 15 students get appointments
            num_appointments = random.randint(1, 3)
            for _ in range(num_appointments):
                days_ahead = random.randint(-30, 30)
                status = random.choice(statuses)
                
                appointment = Appointment.objects.create(
                    student=student,
                    doctor=random.choice(doctors) if status != 'pending' else None,
                    service_type=random.choice(services),
                    preferred_date=timezone.now().date() + timedelta(days=days_ahead),
                    preferred_time_slot=random.choice(['morning', 'afternoon']),
                    reason='Sample appointment reason',
                    emergency_contact_name=student.emergency_contact_name,
                    emergency_contact_number=student.emergency_contact_number,
                    status=status,
                    approved_by=random.choice(doctors) if status != 'pending' else None,
                    approved_at=timezone.now() if status != 'pending' else None,
                )
                count += 1
        
        return count
    
    def create_templates(self):
        templates_data = [
            {
                'name': 'Medical Certificate',
                'type': 'medical_certificate',
                'html': '''
                <div style="text-align: center;">
                    <h1>MEDICAL CERTIFICATE</h1>
                    <p>Certificate No: {{certificate_number}}</p>
                </div>
                <p>Date: {{date_issued}}</p>
                <p>TO WHOM IT MAY CONCERN:</p>
                <p>This is to certify that <strong>{{student_name}}</strong>, 
                Student ID: <strong>{{student_id}}</strong>, was examined on {{date}}.</p>
                <p>Diagnosis: {{diagnosis}}</p>
                <p>This certificate is issued upon request.</p>
                <div style="margin-top: 50px;">
                    <p>{{doctor_name}}<br>{{doctor_license}}</p>
                </div>
                '''
            },
            {
                'name': 'Medical Clearance',
                'type': 'medical_clearance',
                'html': '''
                <div style="text-align: center;">
                    <h1>MEDICAL CLEARANCE</h1>
                </div>
                <p>This is to certify that <strong>{{student_name}}</strong> 
                is medically cleared for {{purpose}}.</p>
                '''
            },
        ]
        
        count = 0
        for data in templates_data:
            Template.objects.get_or_create(
                name=data['name'],
                defaults={
                    'template_type': data['type'],
                    'template_html': data['html'],
                    'is_active': True,
                    'is_default': True,
                }
            )
            count += 1
        
        return count