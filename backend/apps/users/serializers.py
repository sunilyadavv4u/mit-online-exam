"""Serializers for users and profile management."""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import StudentProfile, TeacherProfile, User, UserRole


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = (
            'enrollment_id', 'course', 'batch', 'date_of_birth',
            'address', 'guardian_name', 'guardian_phone',
        )
        read_only_fields = ('enrollment_id',)


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = (
            'employee_id', 'designation', 'department', 'expertise',
            'years_of_experience', 'linkedin',
        )
        read_only_fields = ('employee_id',)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    student_profile = StudentProfileSerializer(read_only=True)
    teacher_profile = TeacherProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'avatar', 'bio', 'is_active',
            'is_email_verified', 'created_at',
            'student_profile', 'teacher_profile',
        )
        read_only_fields = (
            'id', 'role', 'is_active', 'is_email_verified',
            'created_at', 'student_profile', 'teacher_profile',
        )


class UserAdminSerializer(UserSerializer):
    """Allows super-admins to set the role explicitly."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('id', 'is_email_verified', 'created_at',
                            'student_profile', 'teacher_profile')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=[(UserRole.STUDENT, 'Student'), (UserRole.TEACHER, 'Teacher')],
        default=UserRole.STUDENT,
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone',
                  'password', 'password_confirm', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
