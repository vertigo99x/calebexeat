from django.db import models

from accounts.models import Students, Users
import uuid
from django.utils import timezone
from django.conf import settings

status = [
    ('pending','pending'),
    ('approved','approved'),
    ('rejected','rejected'),
]

choices = [('primary','primary'),('danger','danger'),('success','success')]

class Forms(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Students, on_delete=models.CASCADE,null=False)
    exeat_duration = models.CharField(null=False, blank=False, max_length=255)
    exeat_description = models.TextField(null=False, blank=False, max_length=255)
    departure_date = models.DateField(auto_now=False)
    arrival_date = models.DateField(auto_now=False)
    statusPorter = models.CharField(max_length=20, choices=status,null=False,blank=False,default='pending')
    statusStudentAffairs = models.CharField(max_length=20, choices=status,null=False,blank=False,default='pending')
    iscancelled = models.BooleanField(default=False)
    isclearedbySecurity = models.BooleanField(default=False)
    remarks = models.CharField(null=True, blank=True, max_length=255, default='')
    form_added = models.DateTimeField(default=timezone.now)
    date_added = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ('form_added',)
        
        
    def __str__(self):
        return f"{self.uuid} -> {self.student.student.user.username}"
    
    def studentData(self):
        return {
                "uuid":self.student.student.uuid,
                "matric_no":self.student.student.get_user_data()['username'],
                "student_thumbnail":self.student.student.get_image(),
                "student_image":self.student.student.get_thumbnail(),
                "student_level":self.student.student_level,
                "firstname":self.student.student.firstname,
                "middlename":self.student.student.middlename,
                "lastname":self.student.student.lastname,
                "phonenumber":self.student.student.phonenumber,
                "parent_phone_no":self.student.parent_phone_no,
                "alternate_number":self.student.student.alternate_number,
                "department":self.student.get_department(),
                "hostel":self.student.get_hostel(),
                }
        



class Events(models.Model):
    sender = models.ForeignKey(Users,on_delete=models.CASCADE, null=False, blank=False, max_length=255)
    notification = models.TextField(null=False, blank=False, max_length=255)
    receiver = models.CharField(null=False, blank=False, max_length=255)
    tag = models.CharField(null=False, blank=False, max_length=255, default='primary',choices=choices)
    date_added = models.DateTimeField(default=timezone.now)
   
    class Meta:
        ordering = ('-date_added',)
        
    def __str__(self):
        return F"{self.sender.user.username} -> {self.receiver} | {self.date_added}"
   
    def getSenderData(self):
        return {
           "sender_usercat":self.sender.usercat,
           "sender_thumbnail":self.sender.get_thumbnail(),
           "sender_image":self.sender.get_image(),
       }
        
    
class Tickets(models.Model):
    sender = models.ForeignKey(Users,on_delete=models.CASCADE, null=False, blank=False, max_length=255)
    priority = models.IntegerField(null=False, blank=False, default = 3)
    complaint = models.TextField(null=False, blank=False, max_length=500, default = '')
    isHandled = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    
    
    class Meta:
        ordering = ('priority', 'date_added', )
    
    def __str__(self):
        return f'{self.sender.user.username} -> {self.complaint[:20]}... priority: {self.priority} handled?:{self.isHandled}'
    