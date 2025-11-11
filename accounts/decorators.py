"""
Custom decorators for role-based access control.
"""

from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def role_required(*roles):
    """
    Decorator to restrict access to specific user roles.
    
    Usage:
        @role_required('student')
        def student_only_view(request):
            ...
        
        @role_required('doctor', 'admin')
        def staff_only_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect('accounts:login')
            
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(
                    request,
                    'You do not have permission to access this page.'
                )
                # Redirect based on role
                if request.user.is_student():
                    return redirect('students:dashboard')
                elif request.user.is_doctor():
                    return redirect('doctors:dashboard')
                else:
                    return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def student_required(function=None):
    """
    Decorator to restrict access to students only.
    
    Usage:
        @student_required
        def student_view(request):
            ...
    """
    actual_decorator = role_required('student')
    if function:
        return actual_decorator(function)
    return actual_decorator


def doctor_required(function=None):
    """
    Decorator to restrict access to doctors only.
    
    Usage:
        @doctor_required
        def doctor_view(request):
            ...
    """
    actual_decorator = role_required('doctor', 'admin')
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_required(function=None):
    """
    Decorator to restrict access to administrators only.
    
    Usage:
        @admin_required
        def admin_view(request):
            ...
    """
    actual_decorator = role_required('admin')
    if function:
        return actual_decorator(function)
    return actual_decorator


def check_user_role(user, role):
    """
    Check if user has the specified role.
    
    Args:
        user: User instance
        role: Role string ('student', 'doctor', 'admin')
    
    Returns:
        bool: True if user has the role, False otherwise
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    return user.role == role


def check_institutional_email(user):
    """
    Check if user has institutional email.
    
    Args:
        user: User instance
    
    Returns:
        bool: True if user has institutional email
    """
    if not user.is_authenticated:
        return False
    
    return user.has_institutional_email()


def institutional_email_required(function=None):
    """
    Decorator to ensure user has institutional email.
    
    Usage:
        @institutional_email_required
        def view_requiring_institutional_email(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect('accounts:login')
            
            if not request.user.has_institutional_email():
                messages.error(
                    request,
                    'This feature requires an institutional email address.'
                )
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator


class RoleRequiredMixin:
    """
    Mixin for class-based views to restrict access by role.
    
    Usage:
        class StudentDashboardView(RoleRequiredMixin, TemplateView):
            allowed_roles = ['student']
            template_name = 'student/dashboard.html'
    """
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect('accounts:login')
        
        if not self.check_role(request.user):
            messages.error(
                request,
                'You do not have permission to access this page.'
            )
            return self.handle_no_permission(request)
        
        return super().dispatch(request, *args, **kwargs)
    
    def check_role(self, user):
        """Check if user has required role."""
        if user.is_superuser:
            return True
        
        if not self.allowed_roles:
            return True
        
        return user.role in self.allowed_roles
    
    def handle_no_permission(self, request):
        """Redirect user based on their role."""
        if request.user.is_student():
            return redirect('students:dashboard')
        elif request.user.is_doctor():
            return redirect('doctors:dashboard')
        else:
            return redirect('home')


class StudentRequiredMixin(RoleRequiredMixin):
    """Mixin to restrict access to students only."""
    allowed_roles = ['student']


class DoctorRequiredMixin(RoleRequiredMixin):
    """Mixin to restrict access to doctors and admins."""
    allowed_roles = ['doctor', 'admin']


class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin to restrict access to admins only."""
    allowed_roles = ['admin']