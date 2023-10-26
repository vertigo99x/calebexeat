from rest_framework import serializers

from .models import (
    Users,
    Students,
    Porters,
    StudentAffairs
)

from django.contrib.auth.models import User

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            "uuid","get_user_data","usercat",
            "firstname","middlename","lastname",
            "phonenumber","alternate_number","get_image",
            "get_thumbnail","is_active","date_added","getRequestCount"
        ]
        
class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = [
            "get_user_data","home_address",
            "alternate_parent_phone_no",
            "parent_email","student_level","get_department",
            "get_hostel","forms_left_for_today",
        ]
        
class PorterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Porters
        fields = [
            "get_user_data",
            "get_hostel",
        ]
        