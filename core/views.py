from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import *
from django.http import JsonResponse
import json

def check_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        try:
            user = User.objects.get(email=email)
            return JsonResponse({
                'exists': True,
                'is_admin': user.is_superuser
            })
        except User.DoesNotExist:
            return JsonResponse({
                'exists': False,
                'is_admin': False
            })
    return JsonResponse({'error': 'Invalid method'}, status=400)
def home(request):
    profile = Profile.objects.first()
    if not profile:
        profile = Profile.objects.create()
    return render(request, 'home.html', {'profile': profile})

def experience(request):
    experiences = Experience.objects.all()
    return render(request, 'experience.html', {'experiences': experiences})

def projects(request):
    projects_list = Project.objects.all()
    paginator = Paginator(projects_list, 8)
    page = request.GET.get('page')
    projects = paginator.get_page(page)
    return render(request, 'projects.html', {'projects': projects})

def education(request):
    education_list = Education.objects.all()
    return render(request, 'education.html', {'education': education_list})

def resume_view(request):
    resume = Resume.objects.first()
    profile = Profile.objects.first()
    return render(request, 'resume.html', {'resume': resume, 'profile': profile})

def contact(request):
    profile = Profile.objects.first()
    if not profile:
        profile = Profile.objects.create()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message
            )
            messages.success(request, 'Message sent successfully! I will get back to you soon.')
        else:
            messages.error(request, 'Please fill in all fields.')
        
        return redirect('contact')
    
    return render(request, 'contact.html', {'profile': profile})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_superuser=True)
            code = ''.join(random.choices(string.digits, k=6))
            
            PasswordResetToken.objects.create(
                user=user,
                token=code,
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            
            send_mail(
                'Password Reset Code',
                f'Your verification code is: {code}\n\nThis code expires in 10 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            request.session['reset_email'] = email
            messages.success(request, f'Verification code sent to {email}')
            return redirect('verify_code')
        except User.DoesNotExist:
            messages.error(request, 'Email not found')
    
    return render(request, 'forgot_password.html')
def verify_code(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            user = User.objects.get(email=email, is_superuser=True)
            token = PasswordResetToken.objects.filter(
                user=user,
                token=code,
                is_used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')
            
            token.is_used = True
            token.save()
            
            request.session['reset_user_id'] = user.id
            messages.success(request, 'Code verified')
            return redirect('reset_password')
        except:
            messages.error(request, 'Invalid or expired code')
    
    return render(request, 'verify_code.html')

def reset_password(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('reset_password')
        
        user = User.objects.get(id=user_id)
        
        if user.check_password(new_password):
            messages.error(request, 'New password cannot be the same as old password')
            return redirect('reset_password')
        user.set_password(new_password)
        user.save()
        
        del request.session['reset_user_id']
        del request.session['reset_email']
        
        messages.success(request, 'Password reset successful')
        return redirect('login')
    
    return render(request, 'reset_password.html')
@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    profile = Profile.objects.first()
    experiences = Experience.objects.all()
    projects = Project.objects.all()
    education = Education.objects.all()
    resume = Resume.objects.first()
    messages_count = ContactMessage.objects.filter(is_read=False).count()
    recent_messages = ContactMessage.objects.all()[:5]
    
    context = {
        'profile': profile,
        'experiences': experiences,
        'projects': projects,
        'education': education,
        'resume': resume,
        'messages_count': messages_count,
        'recent_messages': recent_messages,
        'experiences_count': experiences.count(),
        'projects_count': projects.count(),
        'education_count': education.count(),
    }
    return render(request, 'dashboard.html', context)

@login_required
def edit_profile(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    profile = Profile.objects.first()
    if not profile:
        profile = Profile.objects.create()
    
    if request.method == 'POST':
        profile.name = request.POST.get('name')
        profile.title = request.POST.get('title')
        profile.bio = request.POST.get('bio')
        profile.github = request.POST.get('github')
        profile.linkedin = request.POST.get('linkedin')
        profile.email = request.POST.get('email')
        profile.location = request.POST.get('location')
        profile.phone = request.POST.get('phone')
        
        tech_stack = request.POST.get('tech_stack', '').split(',')
        profile.tech_stack = [t.strip() for t in tech_stack if t.strip()]
        
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
        
        profile.save()
        messages.success(request, 'Profile updated')
        return redirect('dashboard')
    
    return render(request, 'edit_profile.html', {'profile': profile})

@login_required
def manage_experience(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    experiences = Experience.objects.all()
    context = {
        'experiences': experiences,
        'edit_mode': False
    }
    return render(request, 'manage_experience.html', context)

@login_required
def add_experience(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    if request.method == 'POST':
        Experience.objects.create(
            company=request.POST.get('company'),
            position=request.POST.get('position'),
            location=request.POST.get('location'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') or None,
            description=request.POST.get('description'),
            order=int(request.POST.get('order', 0))
        )
        messages.success(request, 'Experience added successfully')
        return redirect('manage_experience')
    
    return redirect('manage_experience')

@login_required
def edit_experience(request, pk):
    if not request.user.is_superuser:
        return redirect('login')
    
    experience = get_object_or_404(Experience, pk=pk)
    experiences = Experience.objects.all()
    
    if request.method == 'POST':
        experience.company = request.POST.get('company')
        experience.position = request.POST.get('position')
        experience.location = request.POST.get('location')
        experience.start_date = request.POST.get('start_date')
        experience.end_date = request.POST.get('end_date') or None
        experience.description = request.POST.get('description')
        experience.order = int(request.POST.get('order', 0))
        experience.save()
        messages.success(request, 'Experience updated successfully')
        return redirect('manage_experience')
    
    context = {
        'experiences': experiences,
        'experience': experience,
        'edit_mode': True
    }
    return render(request, 'manage_experience.html', context)

@login_required
def delete_experience(request, pk):
    if not request.user.is_superuser:
        return redirect('login')
    
    experience = get_object_or_404(Experience, pk=pk)
    experience.delete()
    messages.success(request, 'Experience deleted successfully')
    return redirect('manage_experience')

@login_required
def manage_projects(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    projects = Project.objects.all()
    context = {
        'projects': projects,
        'edit_mode': False
    }
    return render(request, 'manage_projects.html', context)

@login_required
def add_project(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    if request.method == 'POST':
        project = Project.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            full_description=request.POST.get('full_description'),
            tech_stack=request.POST.get('tech_stack'),
            link=request.POST.get('link'),
            github_link=request.POST.get('github_link'),
            status=request.POST.get('status', 'ongoing'),
            featured=request.POST.get('featured') == 'on',
            order=int(request.POST.get('order', 0))
        )
        
        if 'image' in request.FILES:
            project.image = request.FILES['image']
            project.save()
        
        messages.success(request, 'Project added successfully')
        return redirect('manage_projects')
    
    return redirect('manage_projects')

@login_required
def edit_project(request, pk):
    if not request.user.is_superuser:
        return redirect('login')
    
    project = get_object_or_404(Project, pk=pk)
    projects = Project.objects.all()
    
    if request.method == 'POST':
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')
        project.full_description = request.POST.get('full_description')
        project.tech_stack = request.POST.get('tech_stack')
        project.link = request.POST.get('link')
        project.github_link = request.POST.get('github_link')
        project.status = request.POST.get('status', 'ongoing')
        project.featured = request.POST.get('featured') == 'on'
        project.order = int(request.POST.get('order', 0))
        
        if 'image' in request.FILES:
            project.image = request.FILES['image']
        
        project.save()
        messages.success(request, 'Project updated successfully')
        return redirect('manage_projects')
    
    context = {
        'projects': projects,
        'project': project,
        'edit_mode': True
    }
    return render(request, 'manage_projects.html', context)

@login_required
def delete_project(request, pk):
    if not request.user.is_superuser:
        return redirect('login')
    
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, 'Project deleted successfully')
    return redirect('manage_projects')

@login_required
def manage_education(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    education_list = Education.objects.all()
    context = {
        'education_list': education_list,
        'edit_mode': False
    }
    return render(request, 'manage_education.html', context)

@login_required
def add_education(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    if request.method == 'POST':
        Education.objects.create(
            type=request.POST.get('type'),
            title=request.POST.get('title'),
            institution=request.POST.get('institution'),
            start_year=int(request.POST.get('start_year')),
            end_year=int(request.POST.get('end_year')) if request.POST.get('end_year') else None,
            description=request.POST.get('description'),
            order=int(request.POST.get('order', 0))
        )
        messages.success(request, 'Education entry added successfully')
        return redirect('manage_education')
    
    return redirect('manage_education')

@login_required
def edit_education(request, pk):
    if not request.user.is_superuser:
        return redirect('login')
    
    education = get_object_or_404(Education, pk=pk)
    education_list = Education.objects.all()
    
    if request.method == 'POST':
        education.type = request.POST.get('type')
        education.title = request.POST.get('title')
        education.institution = request.POST.get('institution')
        education.start_year = int(request.POST.get('start_year'))
        education.end_year = int(request.POST.get('end_year')) if request.POST.get('end_year') else None
        education.description = request.POST.get('description')
        education.order = int(request.POST.get('order', 0))
        education.save()
        messages.success(request, 'Education entry updated successfully')
        return redirect('manage_education')
    
    context = {
        'education_list': education_list,
        'education': education,
        'edit_mode': True
    }
    return render(request, 'manage_education.html', context)

@login_required
def delete_education(request, pk):
    if not request.user.is_superuser:
        return redirect('login')
    
    education = get_object_or_404(Education, pk=pk)
    education.delete()
    messages.success(request, 'Education entry deleted successfully')
    return redirect('manage_education')

@login_required
def upload_resume(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    if request.method == 'POST' and request.FILES.get('file'):
        resume = Resume.objects.first()
        if resume:
            resume.file = request.FILES['file']
            resume.save()
        else:
            Resume.objects.create(file=request.FILES['file'])
        
        request.session['resume_success'] = 'Resume uploaded successfully'
    
    return redirect('dashboard')

@login_required
def manage_messages(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    contact_messages = ContactMessage.objects.all().order_by('-created_at')
    paginator = Paginator(contact_messages, 10)
    page = request.GET.get('page')
    messages_page = paginator.get_page(page)
    
    reply_success = request.session.pop('reply_success', None)
    reply_error = request.session.pop('reply_error', None)
    
    context = {
        'messages_list': messages_page,
        'reply_success': reply_success,
        'reply_error': reply_error
    }
    return render(request, 'manage_messages.html', context)
@login_required
def delete_message(request, pk):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        try:
            message = get_object_or_404(ContactMessage, pk=pk)
            message.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Message deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

@login_required
def mark_message_read(request, pk):
    if not request.user.is_superuser:
        return JsonResponse({'success': False}, status=403)
    
    if request.method == 'POST':
        message = get_object_or_404(ContactMessage, pk=pk)
        message.is_read = not message.is_read
        message.save()
        
        return JsonResponse({
            'success': True,
            'is_read': message.is_read
        })
    
    return JsonResponse({'success': False}, status=400)

@login_required
def send_reply(request, pk):
    if not request.user.is_superuser:
        return redirect('login')
    
    message = get_object_or_404(ContactMessage, pk=pk)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        reply_message = request.POST.get('message')
        
        if not subject or not reply_message:
            request.session['reply_error'] = 'Subject and message are required'
            return redirect('manage_messages')
        
        try:
            full_message = f"Dear {message.name},\n\n{reply_message}\n\n---\nBest regards,\nFredrick Makau\n{settings.DEFAULT_FROM_EMAIL}"
            
            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                [message.email],
                fail_silently=False,
            )
            request.session['reply_success'] = f'Reply sent to {message.email}'
        except Exception as e:
            request.session['reply_error'] = f'Email error: {str(e)}'
        
        return redirect('manage_messages')
    
    return redirect('manage_messages')