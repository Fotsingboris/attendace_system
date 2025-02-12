from django.contrib import admin

# Register your models here.
from .models import Employee, Attendance

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('username', 'date_joined', 'last_login')
    search_fields = ('username',)

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out')
    list_filter = ('date', 'employee')
    search_fields = ('employee__username',)

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Attendance, AttendanceAdmin)