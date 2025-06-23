from django.contrib import admin
from .models import Task, TimeSlot, ScheduleEntry,FixedTask

admin.site.register(Task)
admin.site.register(TimeSlot)
admin.site.register(ScheduleEntry)
admin.site.register(FixedTask)
 
 