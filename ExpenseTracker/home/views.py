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

def index(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user=user).order_by('-Date')
        paginator = Paginator(addmoney_info, 4)  # Show 4 records per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Calculate expenses for the cards
        food_drinks_expense = addmoney_info.filter(Category="Food").aggregate(Sum('quantity'))['quantity__sum'] or 0
        bills_payments_expense = addmoney_info.filter(Category="Necessities").aggregate(Sum('quantity'))['quantity__sum'] or 0
        entertainment_expense = addmoney_info.filter(Category="Entertainment").aggregate(Sum('quantity'))['quantity__sum'] or 0

        # Prepare data for the line chart
        chart_data = addmoney_info.values('Date').annotate(
            food_sum=Sum('quantity', filter=Q(Category='Food')),
            shopping_sum=Sum('quantity', filter=Q(Category='Shopping'))
        ).order_by('Date')

        chart_labels = [entry['Date'].strftime('%b %d') for entry in chart_data]
        food_data = [entry['food_sum'] or 0 for entry in chart_data]
        shopping_data = [entry['shopping_sum'] or 0 for entry in chart_data]

        # Prepare data for the bar chart
        bar_chart_data = addmoney_info.values('Category').annotate(
            total_amount=Sum('quantity')
        ).order_by('Category')

        bar_chart_labels = [entry['Category'] for entry in bar_chart_data]
        bar_chart_values = [entry['total_amount'] or 0 for entry in bar_chart_data]

        context = {
            'page_obj': page_obj,
            'food_drinks_expense': food_drinks_expense,
            'bills_payments_expense': bills_payments_expense,
            'entertainment_expense': entertainment_expense,
            'chart_labels': chart_labels,
            'food_data': food_data,
            'shopping_data': shopping_data,
            'bar_chart_labels': bar_chart_labels,
            'bar_chart_values': bar_chart_values,
        }
        return render(request, 'home/index.html', context)
    return redirect('home')

def register(request):
    return render(request, 'home/register.html')

def password(request):
    return render(request,'home/password.html')

def charts(request):
    return render(request,'home/charts.html')

def search(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.GET['fromdate']
        todate = request.GET['todate']
        addmoney = Addmoney_info.objects.filter(user=user, Date__range=[fromdate,todate]).order_by('-Date')
        return render(request,'home/tables.html',{'addmoney':addmoney})
    return redirect('home')

def tables(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        addmoney = Addmoney_info.objects.filter(user=user).order_by('-Date')
        return render(request,'home/tables.html',{'addmoney':addmoney})
    return redirect('home')

def addmoney(request):
    return render(request,'home/addmoney.html')

def profile(request):
    return render(request, 'home/profile.html', {'user': request.user})

def profile_edit(request,id):
    if request.session.has_key('is_logged'):
        add = User.objects.get(id=id)
        # user_id = request.session["user_id"]
        # user1 = User.objects.get(id=user_id)
        return render(request,'home/profile_edit.html',{'add':add})
    return redirect("/home")

def profile_update(request,id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user = User.objects.get(id=id)
            user.first_name = request.POST["fname"]
            user.last_name = request.POST["lname"]
            user.email = request.POST["email"]
            user.userprofile.Savings = request.POST["Savings"]
            user.userprofile.income = request.POST["income"]
            user.userprofile.profession = request.POST["profession"]
            user.userprofile.save()
            user.save()
            return redirect("/profile")
    return redirect("/home") 

def handleSignup(request):
    if request.method == 'POST':
        # Get the post parameters
        uname = request.POST["uname"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        profession = request.POST['profession']
        Savings = request.POST['Savings']
        income = request.POST['income']
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        profile = UserProfile(Savings=Savings, profession=profession, income=income)
        # Check for errors in input
        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already taken, Try something else!!!")
            return redirect("/register")
        if len(uname) > 15:
            messages.error(request, "Username must be max 15 characters, Please try again")
            return redirect("/register")
        if not uname.isalnum():
            messages.error(request, "Username should only contain letters and numbers, Please try again")
            return redirect("/register")
        if pass1 != pass2:
            messages.error(request, "Passwords do not match, Please try again")
            return redirect("/register")
        # Create the user
        user = User.objects.create_user(uname, email, pass1)
        user.first_name = fname
        user.last_name = lname
        user.save()
        profile.user = user
        profile.save()
        messages.success(request, "Your account has been successfully created")
        return redirect("/")
    else:
        return HttpResponse('404 - NOT FOUND')