from django.test import TestCase, Client
from django.utils import timezone
from datetime import datetime
from todo.models import Task

# Create your tests here.


class SampleTestCase(TestCase):
    def test_sample1(self):
        self.assertEqual(1 + 2, 3)


class TaskModelTestCase(TestCase):
    def test_create_task1(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        task = Task(title='task1', due_at=due)
        task.save()
        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task1')
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, due)

    def test_create_task2(self):
        task = Task(title='task2')
        task.save()
        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task2')
        self.assertFalse(task.completed)
        self.assertIsNone(task.due_at, None)

    def test_is_overdue_future(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 6, 30, 0, 0, 0))
        task = Task(title='task1', due_at=due)
        task.save()
        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_past(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title='task1', due_at=due)
        task.save()
        self.assertTrue(task.is_overdue(current))

    def test_is_overdue_none(self):
        current = timezone.make_aware(datetime(2024, 6, 30, 0, 0, 0))
        task = Task(title='task1')
        task.save()
        self.assertFalse(task.is_overdue(current))


class TodoViewTestCase(TestCase):
    def test_index_get(self):
        self.client = Client()
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 0)

    def test_index_post(self):
        self.client = Client()
        data = {
            'title': 'Test Task',
            'due_at': '2024-06-30 23:59:59'
        }
        response = self.client.post('/', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 1)

    def test_index_order_post(self):
        task1 = Task(title='Task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='Task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=post')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task2)
        self.assertEqual(response.context['tasks'][1], task1)

    def test_index_order_due(self):
        task1 = Task(title='Task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='Task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=due')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task1)
        self.assertEqual(response.context['tasks'][1], task2)

    def test_detail_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/detail.html')
        self.assertEqual(response.context['task'], task)

    def test_detail_get_fail(self):
        client = Client()
        response = client.get('/1/')

        self.assertEqual(response.status_code, 404)

class TaskModelTestCase(TestCase):
    # ...existing code...

    def test_create_task_with_tag(self):
        """タグ付きでタスクを作成するテスト"""
        task = Task(title='課題', tag='submit')
        task.save()
        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, '課題')
        self.assertEqual(task.tag, 'submit')
        self.assertEqual(task.get_tag_display(), '作品提出')

class TodoViewTestCase(TestCase):

    def test_index_post_with_tag(self):
        self.client = Client()
        data = {
            'title': 'プログラミング課題',
            'due_at': '2024-06-30 23:59:59',
            'tag': 'coding'
        }
        response = self.client.post('/', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        
        task = response.context['tasks'][0]
        self.assertEqual(task.tag, 'coding')
        self.assertEqual(task.get_tag_display(), 'コーディング')

    def test_index_filter_by_tag(self):
        # テスト用のタスクを作成
        task1 = Task(title='課題1', tag='coding')
        task1.save()
        task2 = Task(title='課題2', tag='submit')
        task2.save()
        
        client = Client()
        response = client.get('/?tag=coding')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0].tag, 'coding')