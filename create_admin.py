import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mik_edu.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def create_admin():
    username = 'admin'
    password = 'adminpass'
    email = 'admin@example.com'
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password, role='admin')
        print('Created superuser', username)
    else:
        print('Superuser already exists')

if __name__ == '__main__':
    create_admin()
