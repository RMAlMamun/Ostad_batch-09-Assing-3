from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import Task


class TaskModelTest(TestCase):
    """Test the Task model"""
    
    def setUp(self):
        self.task = Task.objects.create(
            title="Test Task",
            description="This is a test task",
            completed=False
        )
    
    def test_task_creation(self):
        """Test that a task can be created"""
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.description, "This is a test task")
        self.assertFalse(self.task.completed)
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)
    
    def test_task_str(self):
        """Test the __str__ method"""
        self.assertEqual(str(self.task), "Test Task")
    
    def test_task_with_due_date(self):
        """Test task with due date"""
        future_date = date.today() + timedelta(days=7)
        task = Task.objects.create(
            title="Task with due date",
            due_date=future_date
        )
        self.assertEqual(task.due_date, future_date)
    
    def test_task_ordering(self):
        """Test that tasks are ordered by created_at descending"""
        task1 = Task.objects.create(title="First Task")
        task2 = Task.objects.create(title="Second Task")
        
        tasks = list(Task.objects.all())
        # Most recent first
        self.assertEqual(tasks[0].title, "Second Task")
        self.assertEqual(tasks[1].title, "First Task")


class TaskViewsTest(TestCase):
    """Test the task views"""
    
    def setUp(self):
        self.client = Client()
        self.task = Task.objects.create(
            title="Test Task",
            description="Test description"
        )
    
    def test_task_list_view(self):
        """Test the task list view"""
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")
        self.assertTemplateUsed(response, 'tasks/task_list.html')
    
    def test_task_list_filter_active(self):
        """Test filtering active tasks"""
        completed_task = Task.objects.create(
            title="Completed Task",
            completed=True
        )
        
        response = self.client.get(reverse('tasks:task_list') + '?filter=active')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")
        self.assertNotContains(response, "Completed Task")
    
    def test_task_list_filter_completed(self):
        """Test filtering completed tasks"""
        completed_task = Task.objects.create(
            title="Completed Task",
            completed=True
        )
        
        response = self.client.get(reverse('tasks:task_list') + '?filter=completed')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Completed Task")
        self.assertNotContains(response, "Test Task")
    
    def test_task_create_view_get(self):
        """Test GET request to create task view"""
        response = self.client.get(reverse('tasks:task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_form.html')
    
    def test_task_create_view_post(self):
        """Test POST request to create task"""
        response = self.client.post(reverse('tasks:task_create'), {
            'title': 'New Task',
            'description': 'New description',
            'completed': False
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Task.objects.filter(title='New Task').exists())
    
    def test_task_update_view_get(self):
        """Test GET request to update task view"""
        response = self.client.get(reverse('tasks:task_update', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_form.html')
        self.assertContains(response, "Test Task")
    
    def test_task_update_view_post(self):
        """Test POST request to update task"""
        response = self.client.post(reverse('tasks:task_update', args=[self.task.pk]), {
            'title': 'Updated Task',
            'description': 'Updated description',
            'completed': False
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
    
    def test_task_delete_view_get(self):
        """Test GET request to delete confirmation view"""
        response = self.client.get(reverse('tasks:task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_confirm_delete.html')
        self.assertContains(response, "Test Task")
    
    def test_task_delete_view_post(self):
        """Test POST request to delete task"""
        task_pk = self.task.pk
        response = self.client.post(reverse('tasks:task_delete', args=[task_pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(Task.objects.filter(pk=task_pk).exists())
    
    def test_task_toggle_view(self):
        """Test toggle task completion"""
        initial_status = self.task.completed
        response = self.client.post(reverse('tasks:task_toggle', args=[self.task.pk]), {
            'X-Requested-With': 'XMLHttpRequest'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.completed, initial_status)
    
    def test_task_toggle_view_non_ajax(self):
        """Test toggle task completion without AJAX (fallback)"""
        initial_status = self.task.completed
        response = self.client.post(reverse('tasks:task_toggle', args=[self.task.pk]))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.completed, initial_status)


class TaskFormTest(TestCase):
    """Test the Task form"""
    
    def test_task_form_valid(self):
        """Test valid form submission"""
        from .forms import TaskForm
        
        form_data = {
            'title': 'Valid Task',
            'description': 'Valid description',
            'completed': False
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_task_form_empty_title(self):
        """Test form validation with empty title"""
        from .forms import TaskForm
        
        form_data = {
            'title': '',
            'description': 'Some description',
            'completed': False
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
