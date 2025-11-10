"""
Signals for students app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import StudentProfile

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, **kwargs):
    """
    Create StudentProfile when a User with role='student' is created.
    Note: Profile still needs to be completed by the student.
    """
    if created and instance.role == 'student':
        # Don't create here - let student fill registration form
        pass