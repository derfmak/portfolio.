from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os
import uuid

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

class Profile(models.Model):
    name = models.CharField(max_length=100, default='FREDRICK MAKAU')
    title = models.CharField(max_length=200, default='WEB DEVELOPER | SOFTWARE QUALITY ASSURANCE')
    bio = models.TextField()
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    github = models.URLField(default='https://github.com/fredrickmakau')
    linkedin = models.URLField(default='https://linkedin.com/in/fredrick-makau-04312b220')
    email = models.EmailField(default='fredrickwambua129@gmail.com')
    location = models.CharField(max_length=200, default='Nairobi, Kenya')
    phone = models.CharField(max_length=20, default='+254 740618550')
    tech_stack = models.JSONField(default=list)

class Experience(models.Model):
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-start_date']

class Project(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=300)
    full_description = models.TextField(blank=True)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    link = models.URLField(blank=True)
    github_link = models.URLField(blank=True)
    tech_stack = models.CharField(max_length=300)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

class Education(models.Model):
    EDUCATION_TYPES = [
        ('degree', 'Degree'),
        ('certification', 'Certification'),
    ]
    type = models.CharField(max_length=20, choices=EDUCATION_TYPES)
    title = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-end_year']

class Resume(models.Model):
    file = models.FileField(
        upload_to='resume/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    uploaded_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old = Resume.objects.get(pk=self.pk)
            if old.file and old.file != self.file:
                if os.path.isfile(old.file.path):
                    os.remove(old.file.path)
        super().save(*args, **kwargs)

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']