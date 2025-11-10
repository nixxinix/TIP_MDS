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