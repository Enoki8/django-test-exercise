from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User   # いいね機能のために追加した

# Create your models here.


class Task(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    TASK_TAG = [
        ('coding','コーディング'),
        ('submit', '作品提出'),
        ('presentation', '発表'),
        ('other', 'その他'),
    ]
    tag = models.CharField(max_length=20, choices=TASK_TAG, default='other')
    liked_users = models.ManyToManyField(User, related_name='liked_tasks', blank=True)

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt
    
    def like_count(self):
        return self.liked_users.count()
