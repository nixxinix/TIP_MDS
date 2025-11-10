"""
Management command to send appointment reminders.
Should be run daily via cron job.
"""

from django.core.management.base import BaseCommand
from notifications.services import send_appointment_reminders, mark_expired_notifications


class Command(BaseCommand):
    help = 'Send appointment reminders and clean up expired notifications'
    
    def handle(self, *args, **options):
        self.stdout.write('Sending appointment reminders...')
        
        # Send reminders
        reminder_count = send_appointment_reminders()
        self.stdout.write(
            self.style.SUCCESS(f'✓ Sent {reminder_count} appointment reminder(s)')
        )
        
        # Mark expired notifications
        self.stdout.write('Marking expired notifications...')
        expired_count = mark_expired_notifications()
        self.stdout.write(
            self.style.SUCCESS(f'✓ Marked {expired_count} expired notification(s) as read')
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Reminder task completed!'))