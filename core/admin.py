from django.contrib import admin
from django import forms
from .models import Profile, Experience, Project, Education, Resume, ContactMessage

class ResumeAdminForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']

class ProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not Profile.objects.exists()

class ResumeAdmin(admin.ModelAdmin):
    form = ResumeAdminForm
    
    def has_add_permission(self, request):
        return not Resume.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Experience)
admin.site.register(Project)
admin.site.register(Education)
admin.site.register(Resume, ResumeAdmin)
admin.site.register(ContactMessage)