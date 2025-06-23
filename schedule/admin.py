from django.contrib import admin
from .models import Task, TimeSlot, ScheduleEntry

admin.site.register(Task)
admin.site.register(TimeSlot)
admin.site.register(ScheduleEntry)
