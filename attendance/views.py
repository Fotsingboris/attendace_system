

import base64
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from .models import Employee, Attendance
from .utils import get_face_embedding, verify_face

from django.contrib.admin.views.decorators import staff_member_required
from datetime import date, datetime
from django.db import transaction


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        image_data = request.POST.get("image")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("register")

        if not image_data:
            messages.error(request, "Please allow camera access and try again.")
            return redirect("register")

        try:
            # Convert Base64 image to file
            format, imgstr = image_data.split(";base64,")
            ext = format.split("/")[-1]
            image_file = ContentFile(base64.b64decode(imgstr), name=f"{username}.{ext}")

            # Extract face embedding
            embedding = get_face_embedding(image_file)
            if embedding is None:
                messages.error(request, "Face not detected. Please adjust your position and try again.")
                return redirect("register")

            with transaction.atomic():  # Ensures data consistency
                # Create Employee with hashed password
                user = Employee.objects.create_user(username=username)
                user.set_password(password)  # Ensures password is properly hashed
                user.face_embedding = embedding.tobytes()  # Store the face embedding
                user.save()

            messages.success(request, "Registration successful! You can now log in.")
            return redirect("login")

        except ValueError as ve:
            messages.error(request, f"Value error: {str(ve)}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

        return redirect("register")

    return render(request, "attendance/register.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, "Login Sucessfull")
            return redirect("dashboard")
        messages.error(request, "Invalid credentials.")
    
    return render(request, "attendance/login.html")


@login_required
def mark_attendance(request):
    if request.method == "POST":
        image_data = request.POST.get("image")

        if not image_data:
            messages.error(request, "Please provide an image.")
            return redirect("dashboard")

        try:
            format, imgstr = image_data.split(";base64,")
            ext = format.split("/")[-1]
            image_file = ContentFile(base64.b64decode(imgstr), name=f"temp.{ext}")

            user = request.user

            if verify_face(user.face_embedding, image_file):
                today = datetime.today().date()

                with transaction.atomic():  # Ensures atomic database transaction
                    attendance, created = Attendance.objects.get_or_create(employee=user, date=today)

                    if not attendance.check_in:
                        attendance.check_in = datetime.now().time()
                        messages.success(request, "Check-in successful!")
                    else:
                        attendance.check_out = datetime.now().time()
                        messages.success(request, "Check-out successful!")

                    attendance.save()
            else:
                messages.error(request, "Face not recognized!")

        except ValueError as ve:
            messages.error(request, f"Value error: {str(ve)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect("dashboard")

    return redirect("dashboard")

@login_required
def dashboard(request):
    # Get today's attendance records for the logged-in user
    records = Attendance.objects.filter(employee=request.user, date=datetime.today().date())
    
    # If you want to access the latest attendance record:
    today_record = records.last() if records.exists() else None
    
    return render(request, 'attendance/dashboard.html', {'records': records, 'today_record': today_record})
def user_logout(request):
    logout(request)
    return redirect("login")


from django.utils.dateparse import parse_date

@staff_member_required
def admin_dashboard(request):
    # Get the selected filter values
    filter_date = request.GET.get('date', None)
    filter_user = request.GET.get('user', None)
    
    # Set default values for filters if none are provided
    today = datetime.today().date()
    filter_date = parse_date(filter_date) if filter_date else today
    
    # Fetch all employees for the user filter dropdown
    users = Employee.objects.all()

    # Filter attendance based on selected date and user
    if filter_user:
        filtered_attendance = Attendance.objects.filter(date=filter_date, employee_id=filter_user)
    else:
        filtered_attendance = Attendance.objects.filter(date=filter_date)

    # Fetch statistics
    total_employees = Employee.objects.count()
    total_attendance = Attendance.objects.count()
    today_attendance = Attendance.objects.filter(date=today).count()
    employees_without_checkin_today = Employee.objects.exclude(
        id__in=Attendance.objects.filter(date=today).values('employee')
    ).count()

    # Pass the context to the template
    context = {
        'total_employees': total_employees,
        'total_attendance': total_attendance,
        'today_attendance': today_attendance,
        'employees_without_checkin_today': employees_without_checkin_today,
        'filtered_attendance_list': filtered_attendance,
        'filter_date': filter_date,
        'filter_user': filter_user,
        'users': users,
    }
    
    return render(request, 'attendance/admin_dashboard.html', context)