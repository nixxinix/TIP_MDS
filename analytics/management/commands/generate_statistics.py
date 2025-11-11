"""
Management command to generate analytics statistics.
Can be run manually or via cron job.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from analytics.services import generate_morbidity_statistics, generate_consultation_statistics


class Command(BaseCommand):
    help = 'Generate analytics statistics for specified period'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            choices=['daily', 'weekly', 'monthly', 'yearly'],
            default='monthly',
            help='Period type for statistics'
        )
        
        parser.add_argument(
            '--date',
            type=str,
            help='Start date (YYYY-MM-DD format). Defaults to current period.'
        )
    
    def handle(self, *args, **options):
        period_type = options['period']
        
        # Determine period dates
        if options['date']:
            from datetime import datetime
            period_start = datetime.strptime(options['date'], '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            if period_type == 'daily':
                period_start = today
            elif period_type == 'weekly':
                period_start = today - timedelta(days=today.weekday())
            elif period_type == 'monthly':
                period_start = today.replace(day=1)
            else:  # yearly
                period_start = today.replace(month=1, day=1)
        
        self.stdout.write(f'Generating {period_type} statistics starting from {period_start}...')
        
        # Generate morbidity statistics
        self.stdout.write('Generating morbidity statistics...')
        morbidity_stats = generate_morbidity_statistics(
            period_type=period_type,
            period_start=period_start
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created {len(morbidity_stats)} morbidity statistics')
        )
        
        # Generate consultation statistics
        self.stdout.write('Generating consultation statistics...')
        consultation_stat = generate_consultation_statistics(
            period_type=period_type,
            period_start=period_start
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created consultation statistic: {consultation_stat}')
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Statistics generation completed!'))