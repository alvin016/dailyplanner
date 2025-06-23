import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import Task, TimeSlot, ScheduleEntry, ReflectionNote

def home(request):
    today = now().date()

    # 判斷是否有選取日期（預設為今天）
    date_str = request.GET.get('date') or request.POST.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    timeslots = TimeSlot.objects.all().order_by('hour', 'minute')
    tasks = Task.objects.filter(date=selected_date)

    if request.method == "POST":
        new_task = request.POST.get('new_task')
        if new_task:
            Task.objects.create(title=new_task, date=selected_date)

        for time in timeslots:
            planned = request.POST.get(f'planned_{time.id}', '').strip()
            actual = request.POST.get(f'actual_{time.id}', '').strip()
            if planned or actual:
                entry, _ = ScheduleEntry.objects.get_or_create(date=selected_date, time_slot=time)
                entry.planned = planned
                entry.actual = actual
                entry.save()
        return redirect(f"/?date={selected_date.isoformat()}")

    entry_dict = {entry.time_slot.id: entry for entry in ScheduleEntry.objects.filter(date=selected_date)}

    # 顯示時間字串（例如 08:30）
    for t in timeslots:
        t.display_time = f"{t.hour:02d}:{t.minute:02d}"

    reflection_note = ReflectionNote.objects.filter(date=selected_date).first()
    reflection = reflection_note.content if reflection_note else ""

    return render(request, "schedule/home.html", {
        "today": selected_date,
        "timeslots": timeslots,
        "tasks": tasks,
        "entry_dict": entry_dict,
        "reflection": reflection,
    })

@csrf_exempt
def autosave(request):
    if request.method == "POST":
        data = json.loads(request.body)
        time_slot_id = data.get("time_slot_id")
        date_str = data.get("date")
        value = data.get("value")
        field = data.get("field")

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid date"}, status=400)

        time_slot = get_object_or_404(TimeSlot, pk=time_slot_id)
        entry, _ = ScheduleEntry.objects.get_or_create(date=date, time_slot=time_slot)

        if field == "planned":
            entry.planned = value
        elif field == "actual":
            entry.actual = value
        else:
            return JsonResponse({"status": "error", "message": "Invalid field"}, status=400)

        entry.save()
        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@csrf_exempt
def autosave_reflection(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        date_str = data.get('date')
        content = data.get('content', '')

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid date'}, status=400)

        note, _ = ReflectionNote.objects.get_or_create(date=date)
        note.content = content
        note.save()

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)

def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST":
        task.title = request.POST.get("title", task.title)
        task.save()
        return redirect("home")
    return render(request, "edit_task.html", {"task": task})

def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    return redirect("home")
