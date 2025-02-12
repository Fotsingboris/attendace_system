from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from .models import Employee, Attendance
from .utils import get_face_embedding, verify_face
import base64
from datetime import datetime

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
    records = Attendance.objects.filter(employee=request.user)
    return render(request, "attendance/dashboard.html", {"records": records})

def user_logout(request):
    logout(request)
    return redirect("login")
