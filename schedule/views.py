import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import Task, TimeSlot, ScheduleEntry, ReflectionNote, FixedTask, FixedTaskStatus

def home(request):
    today = now().date()
    date_str = request.GET.get('date') or request.POST.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    timeslots = TimeSlot.objects.all().order_by('hour', 'minute')
    tasks = Task.objects.filter(date=selected_date).order_by('-id')

    # 處理 POST 新任務與排程儲存
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

    entry_dict = {e.time_slot.id: e for e in ScheduleEntry.objects.filter(date=selected_date)}

    # 顯示時間格式
    for t in timeslots:
        t.display_time = f"{t.hour:02d}:{t.minute:02d}"
        t.start_str = f"{t.hour:02d}:{t.minute:02d}"
        t.end_str = f"{t.hour:02d}:{(t.minute + 59) % 60:02d}"

    # 固定任務狀態 per date
    fixed_tasks_with_status = []
    for ft in FixedTask.objects.all():
        status = FixedTaskStatus.objects.filter(task=ft, date=selected_date).first()
        ft.completed = status.completed if status else False
        fixed_tasks_with_status.append(ft)

    reflection_note = ReflectionNote.objects.filter(date=selected_date).first()
    reflection = reflection_note.content if reflection_note else ""

    return render(request, "schedule/home.html", {
        "today": selected_date,
        "timeslots": timeslots,
        "tasks": tasks,
        "entry_dict": entry_dict,
        "reflection": reflection,
        "fixed_tasks": fixed_tasks_with_status,
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
            time_slot = get_object_or_404(TimeSlot, pk=time_slot_id)
        except Exception:
            return JsonResponse({"status": "error", "message": "Invalid date or time slot"}, status=400)

        entry, _ = ScheduleEntry.objects.get_or_create(date=date, time_slot=time_slot)
        if field == "planned":
            entry.planned = value
        elif field == "actual":
            entry.actual = value
        else:
            return JsonResponse({"status": "error", "message": "Invalid field"}, status=400)

        entry.save()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

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

@csrf_exempt
def toggle_task_completed(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        completed = data.get('completed', False)
        try:
            task = Task.objects.get(pk=task_id)
            task.completed = completed
            task.save()
            return JsonResponse({'status': 'ok'})
        except Task.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

@csrf_exempt
def toggle_fixed_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        completed = data.get('completed', False)
        date_str = data.get('date')
        try:
            task = FixedTask.objects.get(pk=task_id)
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (FixedTask.DoesNotExist, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Invalid task or date'}, status=400)

        status, _ = FixedTaskStatus.objects.get_or_create(task=task, date=date)
        status.completed = completed
        status.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST":
        task.title = request.POST.get("updated_title", task.title)
        task.save()
        return redirect("home")
    return render(request, "edit_task.html", {"task": task})

def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    return redirect("home")
