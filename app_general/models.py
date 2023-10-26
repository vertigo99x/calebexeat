from django.db import models

# Create your models here.

genderchoices = [
    ('male','male'),
    ('female','female')
]


class Colleges(models.Model):
    college = models.CharField(null=False, blank=False, max_length=255)

    def __str__(self):
        return self.college
    
    

class Departments(models.Model):
    college = models.ForeignKey(Colleges, on_delete=models.DO_NOTHING,null=False)
    department = models.CharField(null=False, blank=False, max_length=255)

    def __str__(self):
        return self.department
    


class Hostels(models.Model):
    gender=models.CharField(null=False, blank=False, max_length=255, choices=genderchoices, default = '')
    hostel_name=models.CharField(null=False, blank=False, max_length=255, default = '')
    
    
    class Meta:
        ordering=('hostel_name',)
        
        
    def __str__(self):
        return self.hostel_name + ' hall'

