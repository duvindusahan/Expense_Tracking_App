from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.models import User
from .models import Addmoney_info, UserProfile
from django.core.paginator import Paginator
from django.db.models import Sum, Q
import datetime
from django.http import JsonResponse
from .models import Addmoney_info

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
    
def handlelogin(request):
    if request.method =='POST':
        # get the post parameters
        loginuname = request.POST["loginuname"]
        loginpassword1=request.POST["loginpassword1"]
        user = authenticate(username=loginuname, password=loginpassword1)
        if user is not None:
            dj_login(request, user)
            request.session['is_logged'] = True
            user = request.user.id 
            request.session["user_id"] = user
            messages.success(request, " Successfully logged in")
            return redirect('/index')
        else:
            messages.error(request," Invalid Credentials, Please try again")  
            return redirect("/")  
    return HttpResponse('404-not found')

def handleLogout(request):
        del request.session['is_logged']
        del request.session["user_id"] 
        logout(request)
        messages.success(request, " Successfully logged out")
        return redirect('home')

def addmoney_submission(request):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)
            add_money = request.POST["add_money"]
            quantity = request.POST["quantity"]
            Date = request.POST["Date"]
            Category = request.POST["Category"]
            add = Addmoney_info(user=user1, add_money=add_money, quantity=quantity, Date=Date, Category=Category)
            add.save()
            messages.success(request, "Transaction added successfully")
            return redirect('/index')
    return redirect('/index')

def addmoney_update(request, id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            add = Addmoney_info.objects.get(id=id)
            add.add_money = request.POST["add_money"]
            add.quantity = request.POST["quantity"]
            add.Date = request.POST["Date"]
            add.Category = request.POST["Category"]
            add.save()
            messages.success(request, "Transaction updated successfully")
            return redirect("/index")
    return redirect("/home")  

def expense_edit(request, id):
    if request.session.has_key('is_logged'):
        addmoney_info = Addmoney_info.objects.get(id=id)
        return render(request, 'home/expense_edit.html', {'addmoney_info': addmoney_info})
    return redirect("/home")

def expense_delete(request, id):
    if request.session.has_key('is_logged'):
        addmoney_info = Addmoney_info.objects.get(id=id)
        addmoney_info.delete()
        messages.success(request, "Transaction deleted successfully")
        return redirect("/index")
    return redirect("/home")  

def expense_month(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        todays_date = datetime.date.today()
        one_month_ago = todays_date - datetime.timedelta(days=30)
        addmoney_info = Addmoney_info.objects.filter(user=user, Date__gte=one_month_ago, Date__lte=todays_date)
        total_expense = addmoney_info.filter(add_money="Expense").aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_income = addmoney_info.filter(add_money="Income").aggregate(Sum('quantity'))['quantity__sum'] or 0
        amount_saved = total_income - total_expense
        overspent_amount = max(0, total_expense - user.userprofile.Savings)

        context = {
            'user_profile': user.userprofile,
            'total_expense': total_expense,
            'amount_saved': amount_saved,
            'overspent_amount': overspent_amount
        }
        return render(request, 'home/monthly_expense.html', context)
    return redirect('home')

def stats(request):
    if request.session.has_key('is_logged') :
        todays_date = datetime.date.today()
        one_month_ago = todays_date-datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user = user1,Date__gte=one_month_ago,Date__lte=todays_date)
        sum = 0 
        for i in addmoney_info:
            if i.add_money == 'Expense':
                sum=sum+i.quantity
        addmoney_info.sum = sum
        sum1 = 0 
        for i in addmoney_info:
            if i.add_money == 'Income':
                sum1 =sum1+i.quantity
        addmoney_info.sum1 = sum1
        x= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
        y= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
        if x<0:
            messages.warning(request,'Your expenses exceeded your savings')
            x = 0
        if x>0:
            y = 0
        addmoney_info.x = abs(x)
        addmoney_info.y = abs(y)
        return render(request,'home/stats.html',{'addmoney':addmoney_info})
    
def expense_week(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date-datetime.timedelta(days=7)
    user_id = request.session["user_id"]
    user1 = User.objects.get(id=user_id)
    addmoney = Addmoney_info.objects.filter(user = user1,Date__gte=one_week_ago,Date__lte=todays_date)
    finalrep ={}

    def get_Category(addmoney_info):
        return addmoney_info.Category
    Category_list = list(set(map(get_Category,addmoney)))


    def get_expense_category_amount(Category,add_money):
        quantity = 0 
        filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
        for item in filtered_by_category:
            quantity+=item.quantity
        return quantity

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def weekly(request):
    if request.session.has_key('is_logged') :
        todays_date = datetime.date.today()
        one_week_ago = todays_date-datetime.timedelta(days=7)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user = user1,Date__gte=one_week_ago,Date__lte=todays_date)
        sum = 0 
        for i in addmoney_info:
            if i.add_money == 'Expense':
                sum=sum+i.quantity
        addmoney_info.sum = sum
        sum1 = 0 
        for i in addmoney_info:
            if i.add_money == 'Income':
                sum1 =sum1+i.quantity
        addmoney_info.sum1 = sum1
        x= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
        y= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
        if x<0:
            messages.warning(request,'Your expenses exceeded your savings')
            x = 0
        if x>0:
            y = 0
        addmoney_info.x = abs(x)
        addmoney_info.y = abs(y)
    return render(request,'home/weekly.html',{'addmoney_info':addmoney_info})

def check(request):
    if request.method == 'POST':
        user_exists = User.objects.filter(email=request.POST['email'])
        messages.error(request,"Email not registered, TRY AGAIN!!!")
        return redirect("/reset_password")

def info_year(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        todays_date = datetime.date.today()
        one_year_ago = todays_date - datetime.timedelta(days=365)
        addmoney_info = Addmoney_info.objects.filter(user=user, Date__gte=one_year_ago, Date__lte=todays_date)

        # Calculate total expenses and income
        total_expense = addmoney_info.filter(add_money="Expense").aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_income = addmoney_info.filter(add_money="Income").aggregate(Sum('quantity'))['quantity__sum'] or 0
        amount_saved = total_income - total_expense
        overspent_amount = max(0, total_expense - user.userprofile.Savings)
        net_balance = total_income - total_expense

        # Prepare data for the pie chart
        pie_chart_data = addmoney_info.values('Category').annotate(
            total_amount=Sum('quantity', filter=Q(add_money='Expense'))
        ).order_by('Category')

        pie_chart_labels = [entry['Category'] for entry in pie_chart_data]
        pie_chart_values = [entry['total_amount'] or 0 for entry in pie_chart_data]

        context = {
            'user_profile': user.userprofile,
            'total_expense': total_expense,
            'total_income': total_income,
            'amount_saved': amount_saved,
            'overspent_amount': overspent_amount,
            'net_balance': net_balance,
            'pie_chart_labels': pie_chart_labels,
            'pie_chart_values': pie_chart_values,
            'transactions': addmoney_info,
        }
        return render(request, 'home/yearly_expense.html', context)
    return redirect('home')

def expense_month(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        todays_date = datetime.date.today()
        one_month_ago = todays_date - datetime.timedelta(days=30)
        addmoney_info = Addmoney_info.objects.filter(user=user, Date__gte=one_month_ago, Date__lte=todays_date)
        
        total_expense = addmoney_info.filter(add_money="Expense").aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_income = addmoney_info.filter(add_money="Income").aggregate(Sum('quantity'))['quantity__sum'] or 0
        amount_saved = total_income - total_expense
        overspent_amount = max(0, total_expense - user.userprofile.Savings)
        
        # Prepare data for the pie chart
        pie_chart_data = addmoney_info.values('Category').annotate(total_amount=Sum('quantity')).order_by('Category')
        pie_chart_labels = [entry['Category'] for entry in pie_chart_data]
        pie_chart_values = [entry['total_amount'] or 0 for entry in pie_chart_data]

        context = {
            'user_profile': user.userprofile,
            'total_expense': total_expense,
            'amount_saved': amount_saved,
            'overspent_amount': overspent_amount,
            'transactions': addmoney_info,
            'pie_chart_labels': pie_chart_labels,
            'pie_chart_values': pie_chart_values,
        }
        return render(request, 'home/monthly_expense.html', context)
    return redirect('home')

def info(request):
    if request.session.has_key('is_logged'):
        return render(request, 'home/info.html')
    return redirect('home')

def history(request):
    transactions = Addmoney_info.objects.filter(is_deleted=False)

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date and to_date:
        transactions = transactions.filter(Date__range=[from_date, to_date])

    context = {
        'transactions': transactions,
    }
    return render(request, 'home/history.html', context)