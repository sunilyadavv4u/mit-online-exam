from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import StudentProfile, TeacherProfile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ('-created_at',)
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_email_verified', 'created_at')
    list_filter = ('role', 'is_active', 'is_email_verified')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'avatar', 'bio')}),
        ('Role & permissions', {'fields': ('role', 'is_active', 'is_staff',
                                            'is_superuser', 'is_email_verified',
                                            'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active'),
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'enrollment_id', 'course', 'batch')
    search_fields = ('user__email', 'enrollment_id', 'course', 'batch')


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'designation', 'department')
    search_fields = ('user__email', 'employee_id', 'designation', 'department')
