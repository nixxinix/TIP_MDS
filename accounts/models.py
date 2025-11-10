"""
Custom User model for TIP MDS EMR system.
Uses email as the primary authentication field instead of username.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with admin privileges."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with email authentication and role-based access.
    
    Roles:
    - student: Can view own records, submit forms, book appointments
    - doctor: Can view all records, approve/reject requests, manage appointments
    - admin: Full system access including settings and user management
    """
    
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('doctor', 'Doctor'),
        ('admin', 'Administrator'),
    )
    
    # Remove username, use email instead
    username = None
    
    # Email as the primary identifier
    email = models.EmailField(
        _('email address'),
        unique=True,
        validators=[EmailValidator()],
        help_text=_('Required. Must be a valid @tip.edu.ph email address.')
    )
    
    # Role field for access control
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        help_text=_('User role determines access permissions')
    )
    
    # Additional fields
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Contact number (e.g., +63 912 345 6789)')
    )
    
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    last_login = models.DateTimeField(_('last login'), null=True, blank=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    # Role check methods
    def is_student(self):
        """Check if user is a student."""
        return self.role == 'student'
    
    def is_doctor(self):
        """Check if user is a doctor."""
        return self.role == 'doctor'
    
    def is_admin_user(self):
        """Check if user is an administrator."""
        return self.role == 'admin' or self.is_superuser
    
    def has_institutional_email(self):
        """Check if user has valid institutional email."""
        from django.conf import settings
        domain = settings.INSTITUTIONAL_EMAIL_DOMAIN
        return self.email.endswith(f'@{domain}')
    
    def can_approve_requests(self):
        """Check if user can approve student requests."""
        return self.is_doctor() or self.is_admin_user()
    
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.is_admin_user()


class UserProfile(models.Model):
    """
    Extended user profile information.
    Stores additional details not in the main User model.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text=_('Profile picture')
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text=_('Complete address')
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text=_('Date of birth')
    )
    
    emergency_contact_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Emergency contact person')
    )
    
    emergency_contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Emergency contact number')
    )
    
    emergency_contact_relationship = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Relationship to emergency contact')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"