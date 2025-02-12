from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class Employee(AbstractUser):
    # Add any extra fields here
    employee_id = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    face_embedding = models.BinaryField(null=True, blank=True)  # Store face embeddings as binary data


    # Fix the related_name conflicts
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="employee_groups",  # Change this from "user_set"
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="employee_permissions",  # Change this from "user_set"
        blank=True
    )
    
    def __str__(self):
        return self.username
    
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.username} - {self.date}"

