from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Task
from .forms import TaskForm


def task_list(request):
    """List all tasks with optional filter (all/active/completed)"""
    filter_type = request.GET.get('filter', 'all')
    
    tasks = Task.objects.all()
    
    if filter_type == 'active':
        tasks = tasks.filter(completed=False)
    elif filter_type == 'completed':
        tasks = tasks.filter(completed=True)
    
    context = {
        'tasks': tasks,
        'current_filter': filter_type,
    }
    return render(request, 'tasks/task_list.html', context)


def task_create(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task created successfully!')
            return redirect('tasks:task_list')
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


def task_update(request, pk):
    """Update an existing task"""
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('tasks:task_list')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task, 'action': 'Update'})


def task_delete(request, pk):
    """Delete a task (confirmation page)"""
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('tasks:task_list')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@require_http_methods(["POST"])
def task_toggle(request, pk):
    """Toggle task completion status (AJAX endpoint)"""
    task = get_object_or_404(Task, pk=pk)
    task.completed = not task.completed
    task.save()
    
    # Check if request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'completed': task.completed
        })
    
    # Fallback for non-AJAX requests
    messages.success(request, f'Task marked as {"completed" if task.completed else "active"}!')
    return redirect('tasks:task_list')
