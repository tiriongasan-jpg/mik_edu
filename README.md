# MIK-EDU

Мини-проект учебной платформы на Django.

Локальный запуск (Windows):

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python init_data.py
python create_admin.py
python manage.py runserver
```

Стандартный логин: `admin` / `adminpass` (смените пароль после входа).

Запуск в режиме production на Windows (Waitress + WhiteNoise):

```powershell
venv\Scripts\activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
python run_prod.py
```

Или можно запустить напрямую через `waitress-serve`:

```powershell
venv\Scripts\waitress-serve --port=8000 mik_edu.wsgi:application
```

WhiteNoise обслуживает статические файлы из `STATIC_ROOT`.
