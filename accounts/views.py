from django.shortcuts import render
from django.http import HttpResponse

from asgiref.sync import sync_to_async
import asyncio

from threading import Thread

from .models import (
    Users,
    Students,
    Porters,
    StudentAffairs,
    
)

from .serializers import (
    UsersSerializer,
    StudentsSerializer
)

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q


from django.core.cache import cache
from adrf.views import APIView
from adrf.decorators import api_view
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.views.generic import ListView, DetailView, View

from api.views import getCurrentUser

default_items_per_page = 20
host = settings.MAIN_HOSTNAME


def run_async_function_in_thread(async_function, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_function(*args, **kwargs))
    loop.close()
    return result


def getUsers():
    return Users.objects.all()

class AllUsersView(APIView):
    def get(self, request, format=None):
        users = Users.objects.all()
        serializer = UsersSerializer(users, many= True)
        return Response({'message':users})



class GetStudentData(APIView):
    def get(self, request, matric_no, format=None):
        student = Students.objects.filter(student__user__username = matric_no).get()
        serializer = StudentsSerializer(student)
        return Response(serializer.data)
    

class GetUserData(APIView):
    def get(self, request, format=None):
        try:
            token = request.GET.get('token','')
            if token:
                user = getCurrentUser(token)
                
                if user['usercat'] == 'student':
                    student = Students.objects.filter(student__uuid = user['user_obj'].uuid).get()
                    serializer = StudentsSerializer(student)
                    return Response(serializer.data)
                
                elif user['usercat'] == 'porter' or user['usercat'] == 'saffairs':
                    user = Users.objects.filter(uuid=user['user_obj'].uuid).get()
                    serializer = UsersSerializer(user)
                    return Response(serializer.data)
                
                elif user['usercat'] == 'security':
                    user = Users.objects.filter(uuid=user['user_obj'].uuid).get()
                    serializer = UsersSerializer(user)
                    return Response(serializer.data)
        
            return Response({'message':'no_auth'})
        except Exception as e:
            return Response({'message':{}})




class ChangePassword(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
    
        token = data['token']
        old_password = data['old_password']
        new_password = data['new_password']
        
        user = getCurrentUser(token)
        
        if user:
            user = user['user_obj'].user
            userPassword = user.password
            matchcheck = check_password(old_password, userPassword)
            if matchcheck:
                user.set_password(new_password)
                user.save();
                
                return Response({'message':'success'}, 200)
            
            return Response({'message':'incorrect_old_password'},400)
        
        return Response({"message":"no_auth"})

