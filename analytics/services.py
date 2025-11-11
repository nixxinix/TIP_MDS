"""
Analytics service functions for computing statistics.
"""

from django.db.models import Count, Q, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta, datetime
from students.models import MedicalRecord, StudentProfile
from appointments.models import Appointment
from templates_docs.models import IssuedCertificate, Prescription
from .models import MorbidityStatistic, ConsultationStatistic


def get_top_morbidities(record_type='medical', limit=5, date_from=None, date_to=None):
    """
    Get top N diagnoses by frequency.
    
    Args:
        record_type: 'medical' or 'dental'
        limit: Number of top results to return (default: 5)
        date_from: Start date filter (optional)
        date_to: End date filter (optional)
    
    Returns:
        QuerySet of diagnosis counts
    """
    queryset = MedicalRecord.objects.filter(
        status='approved',
        record_type=record_type
    ).exclude(
        diagnosis__isnull=True
    ).exclude(
        diagnosis=''
    )
    
    # Apply date filters
    if date_from:
        queryset = queryset.filter(visit_date__gte=date_from)
    if date_to:
        queryset = queryset.filter(visit_date__lte=date_to)
    
    # Group by diagnosis and count
    top_diagnoses = queryset.values('diagnosis').annotate(
        total=Count('id')
    ).order_by('-total')[:limit]
    
    # Calculate percentages
    total_cases = sum(item['total'] for item in top_diagnoses)
    
    results = []
    for item in top_diagnoses:
        percentage = (item['total'] / total_cases * 100) if total_cases > 0 else 0
        results.append({
            'diagnosis': item['diagnosis'],
            'count': item['total'],
            'percentage': round(percentage, 2)
        })
    
    return results


def get_consultation_statistics(date_from, date_to):
    """
    Get consultation statistics for a date range.
    
    Args:
        date_from: Start date
        date_to: End date
    
    Returns:
        Dictionary with consultation stats
    """
    # Medical records
    medical_count = MedicalRecord.objects.filter(
        visit_date__gte=date_from,
        visit_date__lte=date_to,
        record_type='medical',
        status='approved'
    ).count()
    
    dental_count = MedicalRecord.objects.filter(
        visit_date__gte=date_from,
        visit_date__lte=date_to,
        record_type='dental',
        status='approved'
    ).count()
    
    # Appointments
    appointments = Appointment.objects.filter(
        preferred_date__gte=date_from,
        preferred_date__lte=date_to
    )
    
    total_appointments = appointments.count()
    completed = appointments.filter(status='completed').count()
    cancelled = appointments.filter(status='cancelled').count()
    no_show = appointments.filter(status='no_show').count()
    
    # Certificates and prescriptions
    certificates = IssuedCertificate.objects.filter(
        date_issued__gte=date_from,
        date_issued__lte=date_to
    ).count()
    
    prescriptions = Prescription.objects.filter(
        date_issued__gte=date_from,
        date_issued__lte=date_to
    ).count()
    
    # New students
    new_students = StudentProfile.objects.filter(
        created_at__gte=date_from,
        created_at__lte=date_to
    ).count()
    
    return {
        'total_consultations': medical_count + dental_count,
        'medical_consultations': medical_count,
        'dental_consultations': dental_count,
        'total_appointments': total_appointments,
        'completed_appointments': completed,
        'cancelled_appointments': cancelled,
        'no_show_appointments': no_show,
        'certificates_issued': certificates,
        'prescriptions_issued': prescriptions,
        'new_students_registered': new_students,
    }


def get_daily_consultation_trend(days=30):
    """
    Get daily consultation counts for the last N days.
    
    Args:
        days: Number of days to include
    
    Returns:
        List of daily consultation counts
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    try:
        daily_data = MedicalRecord.objects.filter(
            visit_date__gte=start_date,
            visit_date__lte=end_date,
            status='approved'
        ).annotate(
            date=TruncDate('visit_date')
        ).values('date', 'record_type').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Format results by date
        results = {}
        for item in daily_data:
            # Add null check and handle potential None values
            if item['date'] is None:
                continue
                
            # Convert date to string safely
            try:
                date_str = item['date'].strftime('%Y-%m-%d') if hasattr(item['date'], 'strftime') else str(item['date'])
            except (AttributeError, TypeError):
                # Fallback: try to convert to date object first
                try:
                    from datetime import date
                    if isinstance(item['date'], str):
                        date_obj = datetime.strptime(item['date'], '%Y-%m-%d').date()
                        date_str = date_obj.strftime('%Y-%m-%d')
                    else:
                        date_str = str(item['date'])
                except Exception:
                    continue
            
            if date_str not in results:
                results[date_str] = {'date': date_str, 'medical': 0, 'dental': 0, 'total': 0}
            
            if item['record_type'] == 'medical':
                results[date_str]['medical'] = item['count']
            else:
                results[date_str]['dental'] = item['count']
            
            results[date_str]['total'] += item['count']
        
        return list(results.values())
    
    except Exception as e:
        # Log the error and return empty list
        print(f"Error in get_daily_consultation_trend: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def get_monthly_consultation_trend(months=12):
    """
    Get monthly consultation counts for the last N months.
    
    Args:
        months: Number of months to include
    
    Returns:
        List of monthly consultation counts
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=months*30)
    
    try:
        monthly_data = MedicalRecord.objects.filter(
            visit_date__gte=start_date,
            visit_date__lte=end_date,
            status='approved'
        ).annotate(
            month=TruncMonth('visit_date')
        ).values('month', 'record_type').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Format results by month
        results = {}
        for item in monthly_data:
            # Add null check
            if item['month'] is None:
                continue
            
            try:
                month_str = item['month'].strftime('%Y-%m')
                month_name = item['month'].strftime('%B %Y')
            except (AttributeError, TypeError):
                continue
            
            if month_str not in results:
                results[month_str] = {
                    'month': month_str,
                    'month_name': month_name,
                    'medical': 0,
                    'dental': 0,
                    'total': 0
                }
            
            if item['record_type'] == 'medical':
                results[month_str]['medical'] = item['count']
            else:
                results[month_str]['dental'] = item['count']
            
            results[month_str]['total'] += item['count']
        
        return list(results.values())
    
    except Exception as e:
        print(f"Error in get_monthly_consultation_trend: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def get_service_distribution(date_from=None, date_to=None):
    """
    Get distribution of appointment service types.
    
    Args:
        date_from: Start date filter (optional)
        date_to: End date filter (optional)
    
    Returns:
        List of service type counts
    """
    queryset = Appointment.objects.filter(status__in=['approved', 'completed'])
    
    if date_from:
        queryset = queryset.filter(preferred_date__gte=date_from)
    if date_to:
        queryset = queryset.filter(preferred_date__lte=date_to)
    
    distribution = queryset.values('service_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    total = sum(item['count'] for item in distribution)
    
    results = []
    for item in distribution:
        percentage = (item['count'] / total * 100) if total > 0 else 0
        results.append({
            'service_type': item['service_type'],
            'service_name': dict(Appointment.SERVICE_TYPE_CHOICES).get(item['service_type'], item['service_type']),
            'count': item['count'],
            'percentage': round(percentage, 2)
        })
    
    return results


def generate_morbidity_statistics(period_type='monthly', period_start=None, period_end=None):
    """
    Generate and save morbidity statistics for a period.
    
    Args:
        period_type: 'daily', 'weekly', 'monthly', or 'yearly'
        period_start: Start date of period
        period_end: End date of period
    
    Returns:
        List of created MorbidityStatistic objects
    """
    if not period_start:
        period_start = timezone.now().date().replace(day=1)
    
    if not period_end:
        if period_type == 'monthly':
            # End of month
            next_month = period_start.replace(day=28) + timedelta(days=4)
            period_end = next_month - timedelta(days=next_month.day)
        else:
            period_end = timezone.now().date()
    
    created_stats = []
    
    # Get top morbidities for medical and dental
    for record_type in ['medical', 'dental']:
        top_morbidities = get_top_morbidities(
            record_type=record_type,
            limit=10,
            date_from=period_start,
            date_to=period_end
        )
        
        for item in top_morbidities:
            stat, created = MorbidityStatistic.objects.update_or_create(
                period_type=period_type,
                period_start=period_start,
                diagnosis=item['diagnosis'],
                record_type=record_type,
                defaults={
                    'period_end': period_end,
                    'case_count': item['count'],
                    'percentage': item['percentage']
                }
            )
            if created:
                created_stats.append(stat)
    
    return created_stats


def generate_consultation_statistics(period_type='monthly', period_start=None, period_end=None):
    """
    Generate and save consultation statistics for a period.
    
    Args:
        period_type: 'daily', 'weekly', 'monthly', or 'yearly'
        period_start: Start date of period
        period_end: End date of period
    
    Returns:
        ConsultationStatistic object
    """
    if not period_start:
        period_start = timezone.now().date().replace(day=1)
    
    if not period_end:
        if period_type == 'monthly':
            next_month = period_start.replace(day=28) + timedelta(days=4)
            period_end = next_month - timedelta(days=next_month.day)
        else:
            period_end = timezone.now().date()
    
    stats_data = get_consultation_statistics(period_start, period_end)
    
    stat, created = ConsultationStatistic.objects.update_or_create(
        period_type=period_type,
        period_start=period_start,
        defaults={
            'period_end': period_end,
            **stats_data
        }
    )
    
    return stat