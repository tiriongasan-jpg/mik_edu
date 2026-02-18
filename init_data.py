import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mik_edu.settings')
django.setup()

from core.models import StudyGroup

names = ['ПНК1', 'ПНК2', 'ДО1', 'ДО2', 'ИСИП']
for n in names:
    StudyGroup.objects.get_or_create(name=n)
print('Initial groups ensured.')
