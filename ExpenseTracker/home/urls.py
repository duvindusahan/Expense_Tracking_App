from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('handleSignup/', views.handleSignup, name='handleSignup'),
    path('handlelogin/', views.handlelogin, name='handlelogin'),
    path('handleLogout/', views.handleLogout, name='handleLogout'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="home/reset_password.html"), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="home/reset_password_sent.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="home/password_reset_form.html"), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="home/password_reset_done.html"), name='password_reset_complete'),
    path('addmoney/', views.addmoney, name='addmoney'),
    path('addmoney_submission/', views.addmoney_submission, name='addmoney_submission'),
    path('expense_edit/<int:id>', views.expense_edit, name='expense_edit'),
    path('<int:id>/addmoney_update/', views.addmoney_update, name="addmoney_update"),
    path('expense_delete/<int:id>', views.expense_delete, name='expense_delete'),
    path('profile/', views.profile, name='profile'),
    path('expense_month/', views.expense_month, name='expense_month'),
    path('weekly/', views.weekly, name='weekly'),
    path('info_year/', views.info_year, name='info_year'),
    path('info/', views.info, name='info'),
    path('history/', views.history, name='history'),
    path('stats/', views.stats, name='stats'),
    path('expense_week/', views.expense_week, name='expense_week'),
    path('check/', views.check, name="check"),
    path('search/', views.search, name="search"),
    path('<int:id>/profile_edit/', views.profile_edit, name="profile_edit"),
    path('<int:id>/profile_update/', views.profile_update, name="profile_update"),
    path('info/', views.info, name="info"),
    path('info_year/', views.info_year, name="info_year"),
]