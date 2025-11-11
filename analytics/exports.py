"""
Export functions for generating CSV and PDF reports.
"""

import csv
from io import StringIO, BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from datetime import datetime


def export_to_csv(data, filename, headers):
    """
    Export data to CSV format.
    
    Args:
        data: List of dictionaries with data
        filename: Name of CSV file
        headers: List of column headers
    
    Returns:
        HttpResponse with CSV file
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(headers)
    
    for row in data:
        writer.writerow([row.get(header, '') for header in headers])
    
    return response


def export_morbidity_report_csv(morbidities, date_from, date_to):
    """
    Export morbidity report to CSV.
    
    Args:
        morbidities: List of morbidity data
        date_from: Start date
        date_to: End date
    
    Returns:
        HttpResponse with CSV
    """
    filename = f"morbidity_report_{date_from}_{date_to}.csv"
    headers = ['Rank', 'Diagnosis', 'Cases', 'Percentage']
    
    data = []
    for idx, item in enumerate(morbidities, 1):
        data.append({
            'Rank': idx,
            'Diagnosis': item.get('diagnosis', ''),
            'Cases': item.get('count', 0),
            'Percentage': f"{item.get('percentage', 0)}%"
        })
    
    return export_to_csv(data, filename, headers)


def export_consultation_report_csv(stats, date_from, date_to):
    """
    Export consultation statistics to CSV.
    
    Args:
        stats: Dictionary with consultation statistics
        date_from: Start date
        date_to: End date
    
    Returns:
        HttpResponse with CSV
    """
    filename = f"consultation_report_{date_from}_{date_to}.csv"
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['TIP MDS EMR - Consultation Report'])
    writer.writerow([f'Period: {date_from} to {date_to}'])
    writer.writerow([])
    
    writer.writerow(['Metric', 'Count'])
    writer.writerow(['Total Consultations', stats.get('total_consultations', 0)])
    writer.writerow(['Medical Consultations', stats.get('medical_consultations', 0)])
    writer.writerow(['Dental Consultations', stats.get('dental_consultations', 0)])
    writer.writerow([])
    writer.writerow(['Total Appointments', stats.get('total_appointments', 0)])
    writer.writerow(['Completed Appointments', stats.get('completed_appointments', 0)])
    writer.writerow(['Cancelled Appointments', stats.get('cancelled_appointments', 0)])
    writer.writerow(['No-Show Appointments', stats.get('no_show_appointments', 0)])
    writer.writerow([])
    writer.writerow(['Certificates Issued', stats.get('certificates_issued', 0)])
    writer.writerow(['Prescriptions Issued', stats.get('prescriptions_issued', 0)])
    writer.writerow(['New Students Registered', stats.get('new_students_registered', 0)])
    
    return response


def export_appointments_report_csv(appointments):
    """
    Export appointments list to CSV.
    
    Args:
        appointments: QuerySet of appointments
    
    Returns:
        HttpResponse with CSV
    """
    filename = f"appointments_report_{datetime.now().strftime('%Y%m%d')}.csv"
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Ticket Number', 'Student ID', 'Student Name',
        'Service Type', 'Preferred Date', 'Time Slot',
        'Doctor', 'Status', 'Created At'
    ])
    
    for apt in appointments:
        writer.writerow([
            apt.ticket_number,
            apt.student.student_id,
            apt.student.user.get_full_name(),
            apt.get_service_type_display(),
            apt.preferred_date.strftime('%Y-%m-%d'),
            apt.get_preferred_time_slot_display(),
            apt.doctor.get_full_name() if apt.doctor else 'Not Assigned',
            apt.get_status_display(),
            apt.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


def export_students_report_csv(students):
    """
    Export student registry to CSV.
    
    Args:
        students: QuerySet of StudentProfile
    
    Returns:
        HttpResponse with CSV
    """
    filename = f"students_report_{datetime.now().strftime('%Y%m%d')}.csv"
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Full Name', 'Email', 'Program',
        'Year Level', 'Contact Number', 'Blood Type',
        'Registered Date', 'Verified'
    ])
    
    for student in students:
        writer.writerow([
            student.student_id,
            student.user.get_full_name(),
            student.user.email,
            student.get_program_display(),
            student.get_year_level_display(),
            student.contact_number,
            student.get_blood_type_display(),
            student.created_at.strftime('%Y-%m-%d'),
            'Yes' if student.is_verified else 'No'
        ])
    
    return response


def export_report_to_pdf(template_name, context, filename):
    """
    Generic PDF export function.
    
    Args:
        template_name: Path to HTML template
        context: Template context dictionary
        filename: Output PDF filename
    
    Returns:
        HttpResponse with PDF
    """
    # Render HTML
    html_string = render_to_string(template_name, context)
    
    # Generate PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Create response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def export_morbidity_report_pdf(morbidities, date_from, date_to, record_type='medical'):
    """
    Export morbidity report to PDF.
    
    Args:
        morbidities: List of morbidity data
        date_from: Start date
        date_to: End date
        record_type: 'medical' or 'dental'
    
    Returns:
        HttpResponse with PDF
    """
    context = {
        'title': f'Top Morbidities Report - {record_type.title()}',
        'date_from': date_from,
        'date_to': date_to,
        'generated_date': datetime.now().strftime('%B %d, %Y %H:%M'),
        'morbidities': morbidities,
        'record_type': record_type,
        'total_cases': sum(item.get('count', 0) for item in morbidities)
    }
    
    filename = f"morbidity_report_{record_type}_{date_from}_{date_to}.pdf"
    
    # Use inline HTML if template doesn't exist
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; text-align: center; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #667eea; color: white; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>TIP MDS EMR</h1>
            <h2>{context['title']}</h2>
            <p>Period: {context['date_from']} to {context['date_to']}</p>
            <p>Generated: {context['generated_date']}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Diagnosis</th>
                    <th>Cases</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for idx, item in enumerate(morbidities, 1):
        html_content += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{item.get('diagnosis', '')}</td>
                    <td>{item.get('count', 0)}</td>
                    <td>{item.get('percentage', 0)}%</td>
                </tr>
        """
    
    html_content += f"""
            </tbody>
        </table>
        
        <div class="footer">
            <p>Total Cases: {context['total_cases']}</p>
            <p>Technological Institute of the Philippines - Medical-Dental Services</p>
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
    html = HTML(string=html_content)
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def export_consultation_report_pdf(stats, date_from, date_to):
    """
    Export consultation statistics to PDF.
    
    Args:
        stats: Dictionary with consultation statistics
        date_from: Start date
        date_to: End date
    
    Returns:
        HttpResponse with PDF
    """
    context = {
        'title': 'Consultation Statistics Report',
        'date_from': date_from,
        'date_to': date_to,
        'generated_date': datetime.now().strftime('%B %d, %Y %H:%M'),
        'stats': stats
    }
    
    filename = f"consultation_report_{date_from}_{date_to}.pdf"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; text-align: center; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px; }}
            .stat-box {{ border: 2px solid #667eea; padding: 20px; border-radius: 8px; }}
            .stat-box h3 {{ margin-top: 0; color: #667eea; }}
            .stat-number {{ font-size: 36px; font-weight: bold; color: #333; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>TIP MDS EMR</h1>
            <h2>{context['title']}</h2>
            <p>Period: {context['date_from']} to {context['date_to']}</p>
            <p>Generated: {context['generated_date']}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-box">
                <h3>Total Consultations</h3>
                <div class="stat-number">{stats.get('total_consultations', 0)}</div>
            </div>
            <div class="stat-box">
                <h3>Medical Consultations</h3>
                <div class="stat-number">{stats.get('medical_consultations', 0)}</div>
            </div>
            <div class="stat-box">
                <h3>Dental Consultations</h3>
                <div class="stat-number">{stats.get('dental_consultations', 0)}</div>
            </div>
            <div class="stat-box">
                <h3>Total Appointments</h3>
                <div class="stat-number">{stats.get('total_appointments', 0)}</div>
            </div>
            <div class="stat-box">
                <h3>Completed Appointments</h3>
                <div class="stat-number">{stats.get('completed_appointments', 0)}</div>
            </div>
            <div class="stat-box">
                <h3>Certificates Issued</h3>
                <div class="stat-number">{stats.get('certificates_issued', 0)}</div>
            </div>
            <div class="stat-box">
                <h3>Prescriptions Issued</h3>
                <div class="stat-number">{stats.get('prescriptions_issued', 0)}</div>
            </div>
            <div class="stat-box">
                <h3>New Students</h3>
                <div class="stat-number">{stats.get('new_students_registered', 0)}</div>
            </div>
        </div>
        
        <div class="footer">
            <p>Technological Institute of the Philippines - Medical-Dental Services</p>
        </div>
    </body>
    </html>
    """
    
    html = HTML(string=html_content)
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response