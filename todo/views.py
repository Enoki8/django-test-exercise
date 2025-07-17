from django.contrib.auth.decorators import login_required  # いいね機能のために追加した
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task


def index(request):
    if request.method == 'POST':
        task = Task(
            title=request.POST['title'],
            due_at=make_aware(parse_datetime(request.POST['due_at']))
        )
        task.save()
    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at')
    context = {
        'tasks': tasks,
    }
    return render(request, 'todo/index.html', context)


def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    context = {
        'task' : task,
    }
    return render(request, 'todo/detail.html', context)

def delete(request, task_id):     # 削除処理を追加
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)

def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))
        task.save()
        return redirect(detail, task_id)
    
    context = {
        'task': task
    }
    return render(request, "todo/edit.html", context)


def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect(index)

@login_required
def toggle_like(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.user in task.liked_users.all():
        task.liked_users.remove(request.user)  # いいね解除
    else:
        task.liked_users.add(request.user)     # いいね

    return redirect('detail', task_id=task.id)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # 登録後ログインページへ
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})