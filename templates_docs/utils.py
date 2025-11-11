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
        'school_address': '363 P. Casal Street, Quiapo, Manila; 1338 Arlegui Street, Quiapo, Manila',
        'school_logo_url': '',  # Add logo URL if available
        
        # Certificate Title (DYNAMIC - This makes the title change based on certificate type!)
        'certificate_title': certificate_data.get('title', 'MEDICAL CERTIFICATE'),
        
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
    # Prepare context data - PASS THE TITLE HERE!
    certificate_data = {
        'title': certificate.title,  # ✅ This makes the title dynamic!
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
        'school_address': '363 P. Casal Street, Quiapo, Manila; 1338 Arlegui Street, Quiapo, Manila',
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
    Return default certificate HTML template with improved formatting.
    Uses dynamic title from context.
    """
    # Get the certificate title (Medical Certificate, Medical Clearance, Dental Certificate)
    cert_title = context.get('certificate_title', 'MEDICAL CERTIFICATE').upper()
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{cert_title}</title>
        <style>
            @page {{
                size: A4;
                margin: 2.5cm 2cm;
            }}
            body {{
                font-family: 'Times New Roman', serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #000;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            .page-wrapper {{
                flex: 1;
                display: flex;
                flex-direction: column;
            }}
            .main-content {{
                flex: 1;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 3px solid #000;
            }}
            .header h1 {{
                font-size: 16pt;
                font-weight: bold;
                margin: 0 0 5px 0;
                letter-spacing: 0.5px;
            }}
            .header .address {{
                font-size: 9pt;
                margin: 3px 0;
                color: #333;
            }}
            .header h2 {{
                font-size: 18pt;
                font-weight: bold;
                margin: 20px 0 0 0;
                letter-spacing: 3px;
            }}
            .date-cert-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 20px 0 30px 0;
                padding-bottom: 15px;
                border-bottom: 1px solid #ddd;
            }}
            .date-issued {{
                font-size: 11pt;
                font-weight: bold;
            }}
            .certificate-number {{
                font-size: 8pt;
                color: #777;
                font-style: italic;
            }}
            .to-whom {{
                margin: 25px 0 20px 0;
                font-weight: bold;
                font-size: 11pt;
            }}
            .content {{
                text-align: justify;
                line-height: 1.8;
            }}
            .certification-text {{
                margin: 20px 0;
                text-indent: 50px;
                text-align: justify;
            }}
            .info-row {{
                margin: 12px 0;
                padding-left: 0;
            }}
            .field-label {{
                font-weight: bold;
                display: inline-block;
                min-width: 110px;
            }}
            .field-value {{
                display: inline;
            }}
            .closing-text {{
                margin: 30px 0 20px 0;
                text-indent: 50px;
                text-align: justify;
            }}
            .signature-section {{
                margin-top: auto;
                padding-top: 60px;
                text-align: center;
            }}
            .signature-line {{
                border-top: 2px solid #000;
                width: 280px;
                margin: 40px auto 8px;
            }}
            .doctor-name {{
                font-weight: bold;
                font-size: 12pt;
                margin: 5px 0;
            }}
            .doctor-details {{
                font-size: 10pt;
                margin: 3px 0;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Technological Institute of the Philippines</h1>
            <p class="address">363 P. Casal Street, Quiapo, Manila; 1338 Arlegui Street, Quiapo, Manila</p>
            <h2>{cert_title}</h2>
        </div>
        
        <div class="date-cert-row">
            <div class="date-issued">
                <span class="field-label">Date Issued:</span>
                <span class="field-value">{context['date_issued']}</span>
            </div>
            <div class="certificate-number">
                Certificate No.: {context['certificate_number']}
            </div>
        </div>
            
            <p class="to-whom">TO WHOM IT MAY CONCERN:</p>
            
            <p class="certification-text">
                This is to certify that <strong>{context['student_name']}</strong>, 
                Student ID: <strong>{context['student_id']}</strong>, 
                {context['program']} - {context['year_level']}, 
                was examined on <strong>{context['date']}</strong>.
            </p>
            
            {f'''<div class="info-row">
                <span class="field-label">Diagnosis:</span>
                <span class="field-value">{context["diagnosis"]}</span>
            </div>''' if context.get('diagnosis') else ''}
            
            {f'''<div class="info-row">
                <span class="field-label">Prescription:</span>
                <span class="field-value">{context["prescription"]}</span>
            </div>''' if context.get('prescription') else ''}
            
            {f'''<div class="info-row">
                <span class="field-label">Remarks:</span>
                <span class="field-value">{context["remarks"]}</span>
            </div>''' if context.get('remarks') else ''}
            
            {f'''<div class="info-row">
                <span class="field-label">Purpose:</span>
                <span class="field-value">{context["purpose"]}</span>
            </div>''' if context.get('purpose') else ''}
            
            <p class="closing-text">
                This certificate is issued upon request for whatever legal purpose it may serve.
            </p>
            
            {f'''<div class="info-row">
                <span class="field-label">Valid Until:</span>
                <span class="field-value">{context["valid_until"]}</span>
            </div>''' if context.get('valid_until') else ''}
        </div>
        
        <div class="signature-section">
            <div class="signature-line"></div>
            <p class="doctor-name">{context['doctor_title']}</p>
            <p class="doctor-details">{context['doctor_specialization']}</p>
            <p class="doctor-details">License No.: {context['doctor_license']}</p>
        </div>
    </body>
    </html>
    """


def get_default_prescription_template(context):
    """
    Return default prescription HTML template with improved formatting.
    """
    # Format medications with line breaks
    medications = context.get('medications', '')
    formatted_meds = medications.replace('\n', '<br>')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Prescription</title>
        <style>
            @page {{
                size: A4;
                margin: 2.5cm 2cm;
            }}
            body {{
                font-family: 'Times New Roman', serif;
                font-size: 12pt;
                line-height: 1.8;
                color: #000;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #000;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                font-size: 18pt;
                font-weight: bold;
                margin: 0 0 8px 0;
            }}
            .header p {{
                font-size: 10pt;
                margin: 5px 0;
            }}
            .header h2 {{
                font-size: 16pt;
                font-weight: bold;
                margin: 25px 0 0 0;
                letter-spacing: 2px;
            }}
            .rx-number {{
                text-align: right;
                font-size: 9pt;
                color: #666;
                margin-bottom: 25px;
            }}
            .patient-info {{
                margin: 20px 0;
            }}
            .patient-info p {{
                margin: 8px 0;
            }}
            .field-label {{
                font-weight: bold;
                display: inline-block;
                min-width: 110px;
            }}
            .rx-symbol {{
                font-size: 42px;
                font-weight: bold;
                color: #2196f3;
                margin: 25px 0 10px 0;
            }}
            .medications {{
                margin: 20px 0 20px 30px;
                line-height: 2;
            }}
            .signature-section {{
                margin-top: 80px;
                text-align: center;
            }}
            .signature-line {{
                border-top: 2px solid #000;
                width: 250px;
                margin: 50px auto 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Technological Institute of the Philippines</h1>
            <p>363 P. Casal Street, Quiapo, Manila; 1338 Arlegui Street, Quiapo, Manila</p>
            <h2>PRESCRIPTION</h2>
        </div>
        
        <div class="rx-number">
            Rx No.: {context['prescription_number']}
        </div>
        
        <div class="patient-info">
            <p><span class="field-label">Date:</span> {context['date_issued']}</p>
            <p><span class="field-label">Patient:</span> {context['student_name']}</p>
            <p><span class="field-label">Student ID:</span> {context['student_id']}</p>
        </div>
        
        <div style="margin-top: 30px;">
            <p><strong>Diagnosis:</strong></p>
            <p style="margin-left: 30px;">{context['diagnosis']}</p>
        </div>
        
        <p class="rx-symbol">℞</p>
        <div class="medications">
            {formatted_meds}
        </div>
        
        {f'<div style="margin-top: 30px;"><p><strong>Instructions:</strong></p><p style="margin-left: 30px;">{context["instructions"]}</p></div>' if context.get('instructions') else ''}
        
        <div class="signature-section">
            <div class="signature-line"></div>
            <p><strong>Dr. {context['doctor_name']}</strong></p>
            <p>License No.: {context['doctor_license']}</p>
        </div>
    </body>
    </html>
    """