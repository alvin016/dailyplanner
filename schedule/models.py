from django.db import models
from django.contrib.auth.models import User  # 若有登入系統

# 每天的固定任務
class FixedTask(models.Model):
    title = models.CharField(max_length=100)
   
    def __str__(self):
        return self.title
    


class FixedTaskStatus(models.Model):
    date = models.DateField()
    task = models.ForeignKey(FixedTask, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('date', 'task')

# 每天的任務項目
class Task(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    completed = models.BooleanField(default=False)
    def __str__(self):
        return self.title

# 時間區段（每小時或半小時）
class TimeSlot(models.Model):
    hour = models.IntegerField()  # 6 ~ 23
    minute = models.IntegerField(default=0)  # 預設 0（整點）

    def __str__(self):
        return f"{self.hour:02d}:{self.minute:02d}"

# 排程記錄：預定與實際
class ScheduleEntry(models.Model):
    date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    planned = models.CharField(max_length=255, blank=True)
    actual = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.date} {self.time_slot}"


class ReflectionNote(models.Model):
    date = models.DateField(unique=True)
    content = models.TextField(blank=True)

    def __str__(self):
        return f"{self.date} 筆記"

