from django.urls import path
from .views import register, user_login, mark_attendance, dashboard, user_logout

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("mark_attendance/", mark_attendance, name="mark_attendance"),
    path("logout/", user_logout, name="logout"),
]
