from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.models import User
from .models import Addmoney_info, UserProfile
from django.core.paginator import Paginator
from django.db.models import Sum, Q
import datetime

def home(request):
    if request.session.has_key('is_logged'):
        return redirect('/index')
    return render(request, 'home/login.html')