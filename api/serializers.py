from .models import Forms, Tickets, Events
from rest_framework import serializers


class StaffFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forms
        fields = [
            "uuid","exeat_duration","exeat_description",
            "departure_date","arrival_date","statusPorter",
            "statusStudentAffairs","iscancelled","isclearedbySecurity",
            "remarks","date_added","studentData"
        ]
        
class StudentFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forms
        fields = [
            "uuid","exeat_duration","exeat_description",
            "departure_date","arrival_date","statusPorter",
            "statusStudentAffairs","iscancelled","isclearedbySecurity",
            "remarks","date_added"
        ]
        

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = ["getSenderData","notification","receiver","tag","date_added"]