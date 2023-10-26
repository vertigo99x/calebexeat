from django.shortcuts import render

from asgiref.sync import sync_to_async
import asyncio

from threading import Thread
import time


from .models import (
    Departments,
    Hostels,
    Colleges
)





from django.core.cache import cache

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.views.generic import ListView, DetailView, View
from datetime import date, datetime, timedelta





class GetColleges(APIView):
    def get(self, request, format=None):
        college_list = [
            {
                x.college:[y.department for y in Departments.objects.filter(college__college = x.college)]
                } 
            for x in Colleges.objects.all()
            ]
        
        return Response(college_list)
            
                
                