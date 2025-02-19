from django.urls import path
from .views import *

urlpatterns = [
    path("register/", register, name="register"),
    path("", user_login, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("mark_attendance/", mark_attendance, name="mark_attendance"),
    path("logout/", user_logout, name="logout"),
    path('admin-dashboard/', admin_dashboard, name="admin_dashboard"),

]
