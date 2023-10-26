from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.conf import settings
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.contrib.auth.models import User, AbstractUser
import uuid

from app_general.models import Colleges, Departments, Hostels


import asyncio
from asgiref.sync import sync_to_async
from concurrent.futures import ThreadPoolExecutor


host = settings.MAIN_HOSTNAME


usercatChoices = [
    ('student','student'),
    ('porter','porter'),
    ('saffairs','saffairs'),
    ('security','security'),
    ('superuser','superuser')
]

genderchoices = [
    ('male','male'),
    ('female','female')
]

levels = [('100','100'),('200','200'),('300','300'),('400','400')]


def run_async_function_in_thread(async_function, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_function(*args, **kwargs))
    loop.close()
    return result



class Users(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    usercat = models.CharField(null=False, blank=False, max_length=255, choices=usercatChoices)
    firstname = models.CharField(null=False, blank=False, max_length=255)
    middlename = models.CharField(null=True, blank=True, max_length=255)
    lastname = models.CharField(null=False, blank=False, max_length=255)
    phonenumber = models.CharField(null=False, blank=False, max_length=255)
    alternate_number = models.CharField(null=True, blank=True, max_length=255)
    image = models.ImageField(upload_to="users/", null=True, blank=True)
    thumbnail = models.ImageField(upload_to="users/cropped_img/", null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    
    class Meta:
        ordering = ('user', 'lastname', )
        
    def __str__(self):
        return self.user.username
    
    def get_user_data(self):
        return {
            'username':self.user.username,
            'email':self.user.email,
        }
    
    def get_image(self):
        if self.image:
            return host + self.image.url
        return ""
    
    def make_thumbnail(self, image, size=(96, 96)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)
        
        thumb_io = BytesIO()
        img.save(thumb_io, "JPEG", quality=85)
        thumbnail = File(thumb_io, name=image.name)
        
        return thumbnail
    
    def get_thumbnail(self):
        if self.thumbnail:
            return host + self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                return host + self.thumbnail.url
            else:
                return ''
    
    def getRequestCount(self):
        from api.models import Forms

        if self.usercat == "student":
            forms = Forms.objects.filter(student__student__uuid=self.uuid)
        
            approved = forms.filter(statusPorter='approved', statusStudentAffairs='approved')[:1000].count()
            pending = forms.filter(Q(statusPorter='pending') | Q(statusStudentAffairs='pending'), iscancelled=False)[:1000].count()
            rejected = forms.filter(Q(statusPorter='rejected') | Q(statusStudentAffairs='rejected'))[:1000].count()
            return {
                "pending":pending,
                "approved":approved,
                "rejected":rejected
            }
            
        elif self.usercat == 'porter':
            yesterday = date.today() - timedelta(days = 1)
            porterInfo = Porters.objects.filter(porter__uuid=self.uuid).get()
            forms = Forms.objects.filter(student__hostel__hostel_name=porterInfo.hostel.hostel_name, iscancelled=False)
            print(forms, porterInfo.hostel)
            approved = forms.filter(statusPorter='approved')[:1000].count()
            pending = forms.filter(statusPorter='pending')[:1000].count()
            rejected = forms.filter(statusPorter='rejected')[:1000].count()
            return {
                "pending":pending,
                "approved":approved,
                "rejected":rejected
            }
            
        elif self.usercat == 'saffairs':
            yesterday = date.today() - timedelta(days = 1)
            forms = Forms.objects
        
            approved = forms.filter(statusStudentAffairs='approved')[:1000].count()
            pending = forms.filter(statusStudentAffairs='pending', iscancelled=False)[:1000].count()
            rejected = forms.filter(statusStudentAffairs='rejected')[:1000].count()
            return {
                "pending":pending,
                "approved":approved,
                "rejected":rejected
            }
        
        else:
            return ''
    
    
            

class Students(models.Model):
    student = models.ForeignKey(Users, on_delete=models.CASCADE, null=False, blank=False)
    home_address = models.CharField(null=False, blank=False, max_length=255)
    parent_phone_no = models.CharField(null=False, blank=False, max_length=255)
    alternate_parent_phone_no = models.CharField(null=True, blank=True, max_length=255)
    parent_email = models.EmailField(null=False, blank=False)
    student_level = models.CharField(null=True, blank=True,max_length=5, choices=levels)
    department= models.ForeignKey(Departments, on_delete=models.DO_NOTHING, null=False, blank=False)
    hostel = models.ForeignKey(Hostels,on_delete=models.DO_NOTHING, null=False, blank=False)
    room_number = models.CharField(max_length=255, null=True)
    forms_left_for_today = models.IntegerField(default=3)
    last_form_send_day = models.DateTimeField(null=True, blank=True, default=timezone.now)
   
    class Meta:
        ordering = ('student', )
   
    def __str__(self):
        return self.student.user.username
    
    def get_user_data(self):
        return {
                "uuid":self.student.uuid,
                "get_user_data":self.student.get_user_data(),
                "usercat":self.student.usercat,
                "firstname":self.student.firstname,
                "middlename":self.student.middlename,
                "lastname":self.student.lastname,
                "phonenumber":self.student.phonenumber,
                "parent_phonenumber":self.parent_phone_no,
                "alternate_number":self.student.alternate_number,
                "get_image":self.student.get_image(),
                "get_thumbnail":self.student.get_thumbnail(),
                "is_active":self.student.is_active,
                "date_added":self.student.date_added,
                "getRequestCount":self.student.getRequestCount(),
                }
        
    def get_department(self):
        return {
            "college":self.department.college.college,
            "department":self.department.department
        }
    def get_hostel(self):
        return {
            "hostel_name":self.hostel.hostel_name,
            "gender":self.hostel.gender,
            "room_number":self.room_number
        }

   
    
    
    
class Porters(models.Model):
    porter = models.ForeignKey(Users, on_delete=models.CASCADE, null=False, blank=False)
    hostel = models.ForeignKey(Hostels,on_delete=models.DO_NOTHING, null=False, blank=False)
   
   
    class Meta:
        ordering = ('porter', )
   
    def __str__(self):
        return self.porter.user.username


        
    def get_user_data(self):
        return {
                "uuid":self.porter.uuid,
                "get_user_data":self.porter.get_user_data(),
                "usercat":self.porter.usercat,
                "firstname":self.porter.firstname,
                "middlename":self.porter.middlename,
                "lastname":self.porter.lastname,
                "phonenumber":self.porter.phonenumber,
                "alternate_number":self.porter.alternate_number,
                "get_image":self.porter.get_image(),
                "get_thumbnail":self.porter.get_thumbnail(),
                "is_active":self.porter.is_active,
                "date_added":self.porter.date_added,
                "getRequestCount":self.porter.getRequestCount(),
                }
    
    def get_hostel(self):
        return {
            "hostel_name":self.hostel.hostel_name,
            "gender":self.hostel.gender,
            "room_number":self.room_number
        }
    
    
class StudentAffairs(models.Model):
    studentAffairsOfficer = models.ForeignKey(Users, on_delete=models.CASCADE, null=False, blank=False)
       
    class Meta:
        ordering = ('studentAffairsOfficer', )
   
    def __str__(self):
        return self.studentAffairsOfficer.user.username


    def getRequestCount(self):
        from api.models import Forms

        approved = Forms.objects.filter(statusStudentAffairs='approved').count()
        pending = Forms.objects.filter(statusStudentAffairs='pending').count()
        rejected = Forms.objects.filter(statusStudentAffairs='rejected').count()
        return {
            "pending":pending,
            "approved":approved,
            "rejected":rejected
        }
        