"""
Authentication views for user registration, login, and profile management.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone

from .models import User, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .decorators import role_required


class RegisterView(CreateView):
    """User registration view."""
    
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect if already authenticated
        if request.user.is_authenticated:
            if request.user.is_student():
                return redirect('students:dashboard')
            elif request.user.is_doctor():
                return redirect('doctors:dashboard')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Registration successful! Please log in with your credentials.'
        )
        return response
    
    def form_invalid(self, form):
        """Handle form errors."""
        messages.error(
            self.request,
            'Registration failed. Please correct the errors below.'
        )
        return super().form_invalid(form)


def login_view(request):
    """User login view."""
    
    # Redirect if already authenticated
    if request.user.is_authenticated:
        return redirect_after_login(request.user)
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('username')  # username field contains email
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Authenticate user
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session expiry
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires when browser closes
                else:
                    request.session.set_expiry(1209600)  # 2 weeks
                
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                
                # Redirect based on role
                return redirect_after_login(user)
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view."""
    
    user_name = request.user.get_full_name()
    logout(request)
    messages.success(request, f'Goodbye, {user_name}! You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile view."""
    
    user = request.user
    
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile, user=user)
    
    context = {
        'form': form,
        'user': user,
        'profile': profile
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """Change password view."""
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('accounts:change_password')
        
        # Validate new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('accounts:change_password')
        
        # Validate password strength (minimum 8 characters)
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('accounts:change_password')
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        # Update session to prevent logout
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/change_password.html')


def redirect_after_login(user):
    """Redirect user to appropriate dashboard based on role."""
    
    if user.is_student():
        return redirect('students:dashboard')
    elif user.is_doctor() or user.is_admin_user():
        return redirect('doctors:dashboard')
    else:
        return redirect('home')


# API Views (for AJAX requests)
@login_required
def check_email_api(request):
    """API endpoint to check if email is available."""
    
    email = request.GET.get('email', '').lower()
    
    if not email:
        return JsonResponse({'available': False, 'message': 'Email is required'})
    
    # Check institutional domain
    from django.conf import settings
    domain = settings.INSTITUTIONAL_EMAIL_DOMAIN
    
    if not email.endswith(f'@{domain}'):
        return JsonResponse({
            'available': False,
            'message': f'Only {domain} emails are allowed'
        })
    
    # Check if email exists
    exists = User.objects.filter(email=email).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'Email already registered' if exists else 'Email available'
    })


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from .forms import DoctorRegistrationForm


# Admin check function
def is_admin(user):
    """Check if user is admin."""
    return user.is_authenticated and user.is_admin_user()


@login_required
@user_passes_test(is_admin, login_url='doctors:dashboard')
def user_management_view(request):
    """
    User management view - Admin only.
    Shows all users (Admin, Doctor, Student).
    """
    # Get all users ordered by date joined (newest first)
    all_users = User.objects.all().order_by('-date_joined')
    
    # Optional: Filter by role if requested
    role_filter = request.GET.get('role', None)
    if role_filter and role_filter in ['admin', 'doctor', 'student']:
        all_users = all_users.filter(role=role_filter)
    
    context = {
        'users': all_users,
        'role_filter': role_filter,
        'today': timezone.now()
    }
    
    return render(request, 'accounts/user_management.html', context)


@login_required
@user_passes_test(is_admin, login_url='doctors:dashboard')
def add_user_view(request):
    """
    Add new doctor user - Admin only.
    Auto-generates password and shows it to admin.
    """
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            # Get the generated password from the user object
            temp_password = user.temp_password if hasattr(user, 'temp_password') else None
            
            if temp_password:
                messages.success(
                    request,
                    f'Doctor account created successfully for {user.get_full_name()}! '
                    f'Temporary Password: {temp_password} (Please save this and share securely with the doctor)'
                )
            else:
                messages.success(
                    request,
                    f'Doctor account created successfully for {user.get_full_name()}!'
                )
            
            return redirect('doctors:settings')
        else:
            messages.error(
                request,
                'Failed to create account. Please correct the errors below.'
            )
    else:
        form = DoctorRegistrationForm()
    
    context = {
        'form': form,
        'today': timezone.now()
    }
    
    return render(request, 'accounts/add_user.html', context)


@login_required
@user_passes_test(is_admin, login_url='doctors:dashboard')
def view_user_detail(request, user_id):
    """
    View user details - Admin only.
    Shows user information and admin actions (deactivate, reset password).
    """
    user_obj = get_object_or_404(User, id=user_id)
    profile = UserProfile.objects.filter(user=user_obj).first()
    
    context = {
        'user_obj': user_obj,
        'profile': profile,
        'today': timezone.now()
    }
    
    return render(request, 'accounts/view_user.html', context)


@login_required
@user_passes_test(is_admin, login_url='doctors:dashboard')
def deactivate_user(request, user_id):
    """
    Deactivate or reactivate user account - Admin only.
    Requires POST method for security.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('doctors:settings')
    
    user_obj = get_object_or_404(User, id=user_id)
    
    # Prevent admin from deactivating themselves
    if user_obj.id == request.user.id:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('doctors:settings')
    
    # Toggle active status
    if user_obj.is_active:
        user_obj.is_active = False
        action = 'deactivated'
    else:
        user_obj.is_active = True
        action = 'activated'
    
    user_obj.save()
    
    messages.success(
        request,
        f'Account for {user_obj.get_full_name()} has been {action}.'
    )
    
    return redirect('doctors:settings')


@login_required
@user_passes_test(is_admin, login_url='doctors:dashboard')
def reset_user_password(request, user_id):
    """
    Reset user password - Admin only.
    Generates a temporary password and requires POST method.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('doctors:settings')
    
    user_obj = get_object_or_404(User, id=user_id)
    
    # Prevent admin from resetting their own password this way
    if user_obj.id == request.user.id:
        messages.error(
            request,
            'You cannot reset your own password. Use the Change Password form instead.'
        )
        return redirect('doctors:settings')
    
    # Generate temporary password (8 random characters)
    import random
    import string
    temp_password = ''.join(
        random.choices(string.ascii_letters + string.digits, k=12)
    )
    
    # Set new password (hashed)
    user_obj.set_password(temp_password)
    user_obj.save()
    
    messages.success(
        request,
        f'Password reset successful for {user_obj.get_full_name()}. '
        f'Temporary password: {temp_password} (Please save this and share securely)'
    )
    
    return redirect('doctors:settings')