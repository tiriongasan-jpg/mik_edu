from django.db import models
from django.contrib.auth.models import AbstractUser


class StudyGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=200)
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return f"{self.name} ({self.group})"


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    study_group = models.ForeignKey(StudyGroup, null=True, blank=True, on_delete=models.SET_NULL)


class Module(models.Model):
    name = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.CASCADE, related_name='modules')

    def __str__(self):
        return f"{self.name} ({self.subject})"


def lecture_upload_to(instance, filename):
    return f'lectures/{instance.module.subject.group.name}/{instance.module.subject.name}/{filename}'


class Lecture(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=lecture_upload_to)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lectures')
    assigned_groups = models.ManyToManyField(StudyGroup, blank=True)

    def __str__(self):
        return self.title

    @property
    def file_ext(self):
        name = self.file.name.lower()
        if name.endswith('.pdf'):
            return 'pdf'
        if name.endswith('.md') or name.endswith('.markdown'):
            return 'md'
        if name.endswith('.docx'):
            return 'docx'
        return 'other'


class Test(models.Model):
    name = models.CharField(max_length=255)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='tests')
    attempts_limit = models.IntegerField(default=3, help_text='Максимальное количество попыток на прохождение теста')

    def __str__(self):
        return self.name


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text[:50]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class TestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.test} - {self.score}"


class Schedule(models.Model):
    DAY_CHOICES = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (7, 'Воскресенье'),
    ]
    
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    time = models.TimeField(help_text='Время начала занятия')
    subject = models.CharField(max_length=200, help_text='Предмет')
    room = models.CharField(max_length=100, blank=True, help_text='Кабинет/аудитория')
    
    class Meta:
        ordering = ['day_of_week', 'time']
        unique_together = ['group', 'day_of_week', 'time']
    
    def __str__(self):
        day_name = dict(self.DAY_CHOICES)[self.day_of_week]
        return f"{self.group.name} - {day_name} {self.time} - {self.subject}"
