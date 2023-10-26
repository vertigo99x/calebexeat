from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.template.defaulttags import register
from django.utils import timezone

from asgiref.sync import sync_to_async
import asyncio

from threading import Thread
import time

from accounts.models import (
    Users,
    Students,
    Porters,
    StudentAffairs,
)

from .models import (
    Forms, 
    Events,
    Tickets
)


from accounts.serializers import (
    UsersSerializer,
    StudentsSerializer
)

from .serializers import (
    StaffFormSerializer,
    StudentFormSerializer,
    EventSerializer
)

from django.core.cache import cache

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth

from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.authtoken.models import Token
from django.views.generic import ListView, DetailView, View
from datetime import date, datetime, timedelta


default_items_per_page = settings.DEFAULT_ITEMS_PER_PAGE
default_form_limit = settings.DAILY_FORM_LIMIT
host = settings.MAIN_HOSTNAME
startDateCheck = '2023-01-01'



def run_async_function_in_thread(async_function, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_function(*args, **kwargs))
    loop.close()
    return result



def getCurrentUser(token):
    
    try:
        token_data = Token.objects.filter(key=token).get()
        if token_data:
            user = Users.objects.filter(user__id = token_data.user_id).get()
            if user:
                if user.usercat == 'porter':
                    hostel = Porters.objects.filter(porter__uuid=user.uuid).get().hostel
                elif user.usercat == 'student':
                    hostel = Students.objects.filter(student__uuid=user.uuid).get().hostel
                else:
                    hostel = None  
                if hostel:
                    return {
                        "user_obj":user,
                        "username":user.user.username, 
                        "usercat":user.usercat,
                        "hostel":hostel.hostel_name,
                        "gender":hostel.gender
                    }
                return {
                        "user_obj":user,
                        "username":user.user.username, 
                        "usercat":user.usercat,
                        "hostel":None,
                        "gender":None,
                    } 
        return ''
    except Exception:
        pass


def createEvent(arr_dict):
    try:
        for data in arr_dict:
            sender_obj, notification, receiver, tag = data['sender_obj'], data['notification'], data['receiver'], data['tag']
            event = Events.objects.create(
                sender = sender_obj,
                notification=notification,
                receiver=receiver,
                tag=tag,
            )
            event.save()
        return True
    except Exception:
        return False



class FormView(APIView):
    def get(self, request, format=None):
        try:
            token = request.GET.get('token', '')
            order = request.GET.get('order_by','')
            page = request.GET.get('page', 1)
            status = request.GET.get('status', 'pending')
            dept = request.GET.get('dept', '')
            college = request.GET.get('college', '')
            level = request.GET.get('level', '')
            
            dept=dept.lower()
            
            
            if not status or status.lower() not in ['pending', 'approved', 'rejected']:
                status = 'pending'
            
            if order == "recent":
                order = '-date_added'
            elif order == "departure_date":
                order = 'departure_date'
            else:
                order="date_added"
            
            if token:
                user = getCurrentUser(token)
                print(user)
                if user:
                    usercat = user['usercat']
                    if usercat == 'porter':
                        forms = Forms.objects.filter(student__hostel__hostel_name=user['hostel'], iscancelled=False, statusPorter=status, isclearedbySecurity=False).order_by(order)
                        
                        if level:
                            forms = forms.filter(student__student_level=level)
                            
                        if college:
                            forms = forms.filter(student__department__college__college__contains=college)
                        
                        if dept:
                            forms = forms.filter(student__department__department=dept)
                            
                        forms = forms[:1000]
                        
                        paginatedForms = Paginator(forms, int(default_items_per_page))
                        
                        try:
                            paginatedFormspage = paginatedForms.page(page)
                        except Exception:
                            paginatedFormspage = paginatedForms.page(1)
                            page = 1
                            
                        serializer = StaffFormSerializer(paginatedFormspage, many=True)
                        return Response({'data':serializer.data,'total_pages':paginatedForms.num_pages,'page':page}, 200)
                    
                    elif usercat == 'student':
                        forms = Forms.objects.filter(student__student__user__username=user['username']).order_by('-date_added')
                        paginatedForms = Paginator(forms, int(default_items_per_page))
                        
                        try:
                            paginatedFormspage = paginatedForms.page(page)
                        except Exception:
                            paginatedFormspage = paginatedForms.page(1)
                            page = 1
                            
                        serializer = StudentFormSerializer(paginatedFormspage, many=True)
                        return Response({'data':serializer.data,'total_pages':paginatedForms.num_pages,'page':page}, 200)
                    
                    elif usercat == 'saffairs':
                        forms = Forms.objects.filter(iscancelled=False, statusStudentAffairs=status, isclearedbySecurity=False).order_by(order)
                        if level:
                            forms = forms.filter(student__student_level=level)
                            
                        if college:
                            forms = forms.filter(student__department__college__college=college)
                        
                        if dept:
                            forms = forms.filter(student__department__department=dept)
                        
                        forms = forms[:1000]
                        
                        paginatedForms = Paginator(forms, int(default_items_per_page))
                        
                        
                        try:
                            paginatedFormspage = paginatedForms.page(page)
                        except Exception:
                            paginatedFormspage = paginatedForms.page(1)
                            page = 1
                            
                        serializer = StaffFormSerializer(paginatedFormspage, many=True)
                        return Response({'data':serializer.data,'total_pages':paginatedForms.num_pages,'page':page}, 200)
                
                    elif usercat == 'security':
                        forms = Forms.objects.filter(iscancelled=False, statusStudentAffairs='approved', statusPorter='approved', isclearedbySecurity=False).order_by(order)
                        if level:
                            forms = forms.filter(student__student_level=level)
                            
                        if college:
                            forms = forms.filter(student__department__college__college=college)
                        
                        if dept:
                            forms = forms.filter(student__department__department=dept)
                        
                        forms = forms[:1000]
                        
                        paginatedForms = Paginator(forms, int(default_items_per_page))
                        
                        
                        try:
                            paginatedFormspage = paginatedForms.page(page)
                        except Exception:
                            paginatedFormspage = paginatedForms.page(1)
                            page = 1
                            
                        serializer = StaffFormSerializer(paginatedFormspage, many=True)
                        return Response({'data':serializer.data,'total_pages':paginatedForms.num_pages,'page':page}, 200)
                
                return Response({"message":"no_auth"})
            
            return Response(404)
        
        except Exception as e:
            pass
       
    
    
    
    def post(self, request, *args, **kwargs):
        def getStudentObject(uuid):
            try:
                return Students.objects.filter(student__uuid = uuid)[0]
            except IndexError:
                return ''
        
        data = request.data
        token = data['token']
        exeat_type = data['exeat_duration']
        exeat_description = data['exeat_description']
        departure_date = data['departure_date']
        arrival_date = data['arrival_date']
        
        check = getCurrentUser(token)
        if check:
            if check['usercat'] == 'student':
                if token and exeat_description and departure_date and arrival_date and exeat_type:
                    student = getStudentObject(uuid=check['user_obj'].uuid)
                    if student:
                        if student.forms_left_for_today >= 1:
                            form = Forms.objects.create(
                                student = student,
                                exeat_duration = exeat_type,
                                exeat_description = exeat_description,
                                departure_date = departure_date,
                                arrival_date = arrival_date
                            )
                            form.save()
                            
                            Students.objects.filter(student__uuid=check['user_obj'].uuid).update(forms_left_for_today=int(student.forms_left_for_today) - 1)
                            
                            event_arr = [
                                {
                                    "sender_obj":student.student,
                                    "notification":f"{student.student.user.username} sent a request",
                                    "receiver":f"{student.hostel.hostel_name}",
                                    "tag":"primary",
                                },
                                {
                                    "sender_obj":student.student,
                                    "notification":f"{student.student.user.username} sent a request",
                                    "receiver":"saffairs",
                                    "tag":"primary",
                                },
                            ]
                            
                            task = Thread(
                                target=lambda:createEvent(event_arr),
                                daemon=True)
                            task.run()
                            
                            
                            return Response({'message':'success'})
                        else:
                            return Response({'message':"form_limit_reached"})
                    
        return Response({"message":"no_auth"})
        
    
    
class EventView(APIView):
    def get(self, request, format=None, *args, **kwargs):
        try:
            token = request.GET.get('token', '')
            if token:
                user = getCurrentUser(token)
                
                if user:
                    usercat = user['usercat']
                    if usercat == 'porter':
                        events = Events.objects.filter(receiver=user['hostel'])
                        serializer = EventSerializer(events, many=True)
                        return Response(serializer.data)
                    
                    elif usercat == 'student':
                        events = Events.objects.filter(Q(receiver=user['user_obj'].uuid) | Q(receiver=user['username']))
                        serializer = EventSerializer(events, many=True)
                        return Response(serializer.data)
                    
                    elif usercat == 'saffairs':
                        events = Events.objects.filter(receiver='saffairs')
                        serializer = EventSerializer(events, many=True)
                        return Response(serializer.data)
                    
                    
                
                return Response({"message":[]})
            else:
                return Response({"message":"no_auth"})
        except Exception as e:
            pass

    
    
class CancelForm(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        token = data['token']
        form_uid = data['uid']
        
        user = getCurrentUser(token)
        if user and user['usercat'] == 'student':
            Forms.objects.filter(uuid=form_uid).update(iscancelled=True)
            if user['gender'] == 'male':
                acr = "his"
            else:
                acr = "her"
                
            event_arr = [
                {
                    "sender_obj":user['user_obj'],
                    "notification":f"You cancelled your request",
                    "receiver":f"{user['username']}",
                    "tag":"danger",
                },
                {
                    "sender_obj":user['user_obj'],
                    "notification":f"{user['user_obj'].user.username} cancelled {acr} request",
                    "receiver":f"{user['hostel']}",
                    "tag":"danger",
                },
                {
                    "sender_obj":user['user_obj'],
                    "notification":f"{user['user_obj'].user.username} cancelled {acr} request",
                    "receiver":"saffairs",
                    "tag":"danger",
                },
            ]
            
            task = Thread(
                target=lambda:createEvent(event_arr),
                daemon=True)
            task.run()
            
            return Response({'message':'successful'})
        
        return Response({"message":"no_auth"})

    

class SearchForms(APIView):
    def get(self, request, format=None):
        token = request.GET.get('token', '')
        matric_no = request.GET.get('matric', '')
        
        if token:
            user = getCurrentUser(token)
            if user:
                usercat = user['usercat']
                if usercat == 'porter' or usercat == 'saffairs':
                    forms = Forms.objects.filter(student__student__user__username = matric_no).order_by('-date_added')[:10]
                    serializer = StaffFormSerializer(forms, many=True)
                    return Response(serializer.data, 200)
            return Response({"message":"no_auth"})
        
        return Response(404)
    
        
    
class ApproveOrRejectForm(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        token = data['token']
        form_uid = data['uid']
        student_matric = data['student_matric']
        remarks = data['remarks']
        action = data['action'].strip().lower()
        
        if remarks:
            remarks = f"({remarks})"
        
        print(data)
        
        if action == 'approve':
            action = 'approved'
            tag='success'
        elif action == 'reject':
            action = 'rejected'
            tag='danger'
        else:
            return Response({'message':'invalid_action'})
        
        user = getCurrentUser(token)
        if user:
            if user['gender'] == 'male':
                acr = 'Mr'
            elif user['gender'] == 'female':
                acr = "Mrs"
            
            else:
                acr=''
                    
            if user['usercat'] == 'porter':
                
                    
                form = Forms.objects.filter(uuid = form_uid)
                remark = form.get().remarks
                if not remark:
                    remark=''
                else:
                    remark=f'{remark}; '
                    
                form.update(statusPorter=action, remarks=f"{remark}{action} by {acr} {user['user_obj'].lastname} {user['user_obj'].firstname}")
                
                
                event_arr = [
                    {
                        "sender_obj":user['user_obj'],
                        "notification":f"Your Porter {action} Your Request {remarks}",
                        "receiver":f"{student_matric}",
                        "tag":tag,
                    },
                    {
                        "sender_obj":user['user_obj'],
                        "notification":f"You {action} a request from {student_matric.replace('-', '/')} {remarks}",
                        "receiver":f"{user['hostel']}",
                        "tag":tag,
                    },
                    
                ]
                
                task = Thread(
                    target=lambda:createEvent(event_arr),
                    daemon=True)
                task.run()
                
                return Response({'message':'successful'}, 200)
                
            elif user['usercat'] == 'saffairs':
                form = Forms.objects.filter(uuid = form_uid)
                remark = form.get().remarks
                if not remark:
                    remark=''
                else:
                    remark=f'{remark}; '
                form.update(statusStudentAffairs=action, remarks=f"({remark}; {action} by {acr} {user['user_obj'].lastname} {user['user_obj'].firstname})")
                
                
                event_arr = [
                    {
                        "sender_obj":user['user_obj'],
                        "notification":f"Student's Affairs {action} Your Request {remarks}",
                        "receiver":f"{student_matric}",
                        "tag":tag,
                    },
                    
                    {
                        "sender_obj":user['user_obj'],
                        "notification":f"You {action} a request from {student_matric.replace('-', '/')}",
                        "receiver":"saffairs",
                        "tag":tag,
                    },
                ]
                
                task = Thread(
                    target=lambda:createEvent(event_arr),
                    daemon=True)
                task.run()
                
                return Response({'message':'successful'}, 200)
            else:
                return Response({'message':'unauthorized'}, 404)
        
        return Response({"message":"no_auth"})
        




class Logout(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            token = data['token']
            print('waaaa, token',token)
            token = Token.objects.filter(key=token)
            if token:
                token.delete()            
            return Response({'message':'loggged out successfully'})
        except Exception as e:
            return Response({'message':str(e)})

class Logout2(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            token = data['token']
            Token.objects.filter(key=token).delete()
            
            return Response({'message':'loggged out successfully'})
        except Exception:
            return Response({'message':'log out error'})



def autoCancelForms():
    while True:
        try:
            yesterday = date.today() - timedelta(days = 1)
            Forms.objects.filter(
                departure_date__range=[startDateCheck,yesterday]).filter(Q(statusPorter='pending') | Q(statusStudentAffairs='pending'),
                        iscancelled=False, isclearedbySecurity=False).update(
                            iscancelled=True
                        )
        except Exception:
            pass
            
        time.sleep(86400)
     

main_task = Thread(
    target=autoCancelForms,
    daemon=True
)
main_task.start()


    
class FirstLoginView(APIView):
    def get(self, request, *args, **kwargs):
        matric_no = request.GET.get('matric', '')
        today = datetime.now()
        today_date = f"{today.year}-{today.month}-{today.day}"
        student = Students.objects.filter(student__user__username = matric_no)
        if student:
            last_form_sent_date = student.get().last_form_send_day
            if last_form_sent_date and f"{last_form_sent_date}" != today_date:
                student.update(forms_left_for_today=default_form_limit)
                
            return Response(200)
        return Response(200)
            
    

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())

def sessionlogout(request):
    auth.logout(request)
    return redirect('index')
    


class SuperUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "dashboard.html")

    def post(self, request, *args, **kwargs):
        return HttpResponse('POST request!')