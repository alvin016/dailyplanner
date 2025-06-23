from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Task, TimeSlot, ScheduleEntry

def home(request):
    today = now().date()
    # 🗓️ 取得指定日期，若無則為今天
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = now().date()
    else:
        selected_date = now().date()

    timeslots = TimeSlot.objects.order_by('hour', 'minute')

    # 📌 儲存任務
    if request.method == 'POST':
        if 'new_task' in request.POST:
            task_title = request.POST.get('new_task', '').strip()
            if task_title:
                Task.objects.create(title=task_title, date=today)
                
    # 儲存表單資料
    if request.method == 'POST':
        if 'new_task' in request.POST:
            task_title = request.POST.get('new_task', '').strip()
            if task_title:
                Task.objects.create(title=task_title, date=selected_date)
        else:
            for time in timeslots:
                planned_key = f'planned_{time.id}'
                actual_key = f'actual_{time.id}'
                planned = request.POST.get(planned_key, '').strip()
                actual = request.POST.get(actual_key, '').strip()

                entry, _ = ScheduleEntry.objects.get_or_create(date=selected_date, time_slot=time)
                entry.planned = planned
                entry.actual = actual
                entry.save()

        return redirect(f"/?date={selected_date.isoformat()}")

    # 加上 display_time
    for t in timeslots:
        t.display_time = f"{t.hour:02d}:{t.minute:02d}"

    tasks = Task.objects.filter(date=selected_date)
    entries = ScheduleEntry.objects.filter(date=selected_date)
    entry_dict = {e.time_slot.id: e for e in entries}

    return render(request, 'schedule/home.html', {
        'today': selected_date,
        'tasks': tasks,
        'timeslots': timeslots,
        'entry_dict': entry_dict,
    })

def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        new_title = request.POST.get('updated_title', '').strip()
        if new_title:
            task.title = new_title
            task.save()
        return redirect('home')

    return render(request, 'schedule/edit_task.html', {'task': task})


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('home')