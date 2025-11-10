"""
Utility functions for PDF generation and template rendering.
"""

from django.template import Context, Template as DjangoTemplate
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os
from datetime import datetime


def render_template_with_context(template_html, context_data):
    """
    Render HTML template with context data.
    
    Args:
        template_html: HTML template string with {{variables}}
        context_data: Dictionary of variables to replace
    
    Returns:
        Rendered HTML string
    """
    template = DjangoTemplate(template_html)
    context = Context(context_data)
    return template.render(context)


def generate_pdf_from_html(html_content, css_content=None):
    """
    Generate PDF from HTML content using WeasyPrint.
    
    Args:
        html_content: HTML string to convert
        css_content: Optional CSS string for styling
    
    Returns:
        PDF bytes
    """
    # Font configuration for proper rendering
    font_config = FontConfiguration()
    
    # Create HTML object
    html = HTML(string=html_content)
    
    # Create CSS objects if provided
    stylesheets = []
    if css_content:
        stylesheets.append(CSS(string=css_content, font_config=font_config))
    
    # Add default styles
    default_css = """
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.6;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .certificate-number {
            text-align: right;
            font-size: 10pt;
            color: #666;
        }
        .signature-section {
            margin-top: 50px;
            text-align: center;
        }
        .signature-line {
            border-top: 1px solid #000;
            width: 200px;
            margin: 30px auto 5px;
        }
    """
    stylesheets.append(CSS(string=default_css, font_config=font_config))
    
    # Generate PDF
    pdf = html.write_pdf(stylesheets=stylesheets, font_config=font_config)
    
    return pdf


def create_certificate_context(student, doctor, certificate_data):
    """
    Create context dictionary for certificate generation.
    
    Args:
        student: StudentProfile instance
        doctor: User instance (doctor)
        certificate_data: Dict with additional certificate info
    
    Returns:
        Dictionary of context variables
    """
    context = {
        # School Information
        'school_name': 'Technological Institute of the Philippines',
        'school_address': '938 Aurora Blvd, Cubao, Quezon City, Metro Manila',
        'school_logo_url': '',  # Add logo URL if available
        
        # Student Information
        'student_name': student.user.get_full_name(),
        'student_id': student.student_id,
        'program': student.get_program_display(),
        'year_level': student.get_year_level_display(),
        'student_address': student.address,
        
        # Medical Information
        'height': f"{student.height_cm} cm" if student.height_cm else 'N/A',
        'weight': f"{student.weight_kg} kg" if student.weight_kg else 'N/A',
        'blood_type': student.get_blood_type_display(),
        'blood_pressure': certificate_data.get('blood_pressure', 'N/A'),
        'temperature': certificate_data.get('temperature', 'N/A'),
        
        # Doctor Information
        'doctor_name': doctor.get_full_name(),
        'doctor_title': f"Dr. {doctor.get_full_name()}",
        'doctor_license': doctor.doctor_profile.license_number if hasattr(doctor, 'doctor_profile') else '',
        'doctor_specialization': doctor.doctor_profile.get_specialization_display() if hasattr(doctor, 'doctor_profile') else '',
        
        # Certificate Details
        'diagnosis': certificate_data.get('diagnosis', ''),
        'prescription': certificate_data.get('prescription', ''),
        'remarks': certificate_data.get('remarks', ''),
        'purpose': certificate_data.get('purpose', ''),
        'certificate_number': certificate_data.get('certificate_number', ''),
        
        # Dates
        'date': datetime.now().strftime('%B %d, %Y'),
        'date_issued': certificate_data.get('date_issued', datetime.now().strftime('%B %d, %Y')),
        'valid_until': certificate_data.get('valid_until', ''),
        
        # Current timestamp
        'current_year': datetime.now().year,
    }
    
    return context


def generate_certificate_pdf(certificate):
    """
    Generate PDF for an IssuedCertificate instance.
    
    Args:
        certificate: IssuedCertificate instance
    
    Returns:
        ContentFile with PDF data
    """
    # Prepare context data
    certificate_data = {
        'certificate_number': certificate.certificate_number,
        'diagnosis': certificate.diagnosis,
        'prescription': certificate.prescription,
        'remarks': certificate.remarks,
        'purpose': certificate.purpose,
        'date_issued': certificate.date_issued.strftime('%B %d, %Y'),
        'valid_until': certificate.valid_until.strftime('%B %d, %Y') if certificate.valid_until else '',
    }
    
    context = create_certificate_context(
        certificate.student,
        certificate.doctor,
        certificate_data
    )
    
    # Render template
    if certificate.template:
        html_content = render_template_with_context(
            certificate.template.template_html,
            context
        )
        css_content = certificate.template.template_css
    else:
        # Use default template
        html_content = get_default_certificate_template(context)
        css_content = None
    
    # Generate PDF
    pdf_bytes = generate_pdf_from_html(html_content, css_content)
    
    # Create ContentFile
    filename = f"certificate_{certificate.certificate_number}.pdf"
    pdf_file = ContentFile(pdf_bytes, name=filename)
    
    return pdf_file


def generate_prescription_pdf(prescription):
    """
    Generate PDF for a Prescription instance.
    
    Args:
        prescription: Prescription instance
    
    Returns:
        ContentFile with PDF data
    """
    context = {
        'school_name': 'Technological Institute of the Philippines',
        'school_address': '938 Aurora Blvd, Cubao, Quezon City, Metro Manila',
        'prescription_number': prescription.prescription_number,
        'student_name': prescription.student.user.get_full_name(),
        'student_id': prescription.student.student_id,
        'date_issued': prescription.date_issued.strftime('%B %d, %Y'),
        'diagnosis': prescription.diagnosis,
        'medications': prescription.medications,
        'instructions': prescription.instructions,
        'doctor_name': prescription.doctor.get_full_name(),
        'doctor_license': prescription.doctor.doctor_profile.license_number if hasattr(prescription.doctor, 'doctor_profile') else '',
    }
    
    html_content = get_default_prescription_template(context)
    pdf_bytes = generate_pdf_from_html(html_content)
    
    filename = f"prescription_{prescription.prescription_number}.pdf"
    pdf_file = ContentFile(pdf_bytes, name=filename)
    
    return pdf_file


def get_default_certificate_template(context):
    """
    Return default certificate HTML template.
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Medical Certificate</title>
    </head>
    <body>
        <div class="header">
            <h1>{context['school_name']}</h1>
            <p>{context['school_address']}</p>
            <h2 style="margin-top: 30px;">MEDICAL CERTIFICATE</h2>
        </div>
        
        <div class="certificate-number">
            Certificate No.: {context['certificate_number']}
        </div>
        
        <div class="content" style="margin-top: 30px;">
            <p><strong>Date Issued:</strong> {context['date_issued']}</p>
            
            <p style="margin-top: 20px;">TO WHOM IT MAY CONCERN:</p>
            
            <p style="margin-top: 20px;">
                This is to certify that <strong>{context['student_name']}</strong>, 
                Student ID: <strong>{context['student_id']}</strong>, 
                {context['program']} - {context['year_level']}, 
                was examined on {context['date']}.
            </p>
            
            {f'<p><strong>Diagnosis:</strong> {context["diagnosis"]}</p>' if context.get('diagnosis') else ''}
            {f'<p><strong>Prescription:</strong> {context["prescription"]}</p>' if context.get('prescription') else ''}
            {f'<p><strong>Remarks:</strong> {context["remarks"]}</p>' if context.get('remarks') else ''}
            
            <p style="margin-top: 30px;">
                This certificate is issued upon request for whatever legal purpose it may serve.
            </p>
            
            {f'<p><strong>Valid Until:</strong> {context["valid_until"]}</p>' if context.get('valid_until') else ''}
        </div>
        
        <div class="signature-section">
            <div class="signature-line"></div>
            <p><strong>{context['doctor_title']}</strong></p>
            <p>{context['doctor_specialization']}</p>
            <p>License No.: {context['doctor_license']}</p>
        </div>
    </body>
    </html>
    """


def get_default_prescription_template(context):
    """
    Return default prescription HTML template.
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Prescription</title>
    </head>
    <body>
        <div class="header">
            <h1>{context['school_name']}</h1>
            <p>{context['school_address']}</p>
            <h2 style="margin-top: 30px;">PRESCRIPTION</h2>
        </div>
        
        <div class="certificate-number">
            Rx No.: {context['prescription_number']}
        </div>
        
        <div class="content" style="margin-top: 30px;">
            <p><strong>Date:</strong> {context['date_issued']}</p>
            <p><strong>Patient:</strong> {context['student_name']}</p>
            <p><strong>Student ID:</strong> {context['student_id']}</p>
            
            <p style="margin-top: 20px;"><strong>Diagnosis:</strong></p>
            <p>{context['diagnosis']}</p>
            
            <p style="margin-top: 20px;"><strong>Rx:</strong></p>
            <pre style="white-space: pre-wrap; font-family: Arial;">{context['medications']}</pre>
            
            {f'<p style="margin-top: 20px;"><strong>Instructions:</strong></p><p>{context["instructions"]}</p>' if context.get('instructions') else ''}
        </div>
        
        <div class="signature-section">
            <div class="signature-line"></div>
            <p><strong>Dr. {context['doctor_name']}</strong></p>
            <p>License No.: {context['doctor_license']}</p>
        </div>
    </body>
    </html>
    """