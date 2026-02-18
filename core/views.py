import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.conf import settings
from .models import Lecture, Test, Choice, TestAttempt, User, StudyGroup, Module, Question, Subject
import markdown as md

try:
    import mammoth
except Exception:
    mammoth = None


def logout_view(request):
    logout(request)
    return redirect('core:login')


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


# Admin Panel Views
@login_required
@user_passes_test(is_admin)
def admin_schedule(request):
    """Список групп для редактирования расписания"""
    groups = StudyGroup.objects.all().order_by('name')
    return render(request, 'core/admin/schedule_groups.html', {'groups': groups})


@login_required
@user_passes_test(is_admin)
def admin_schedule_group(request, group_id):
    """Расписание конкретной группы"""
    from .models import Schedule
    
    group = get_object_or_404(StudyGroup, id=group_id)
    schedules = Schedule.objects.filter(group=group).order_by('day_of_week', 'time')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            day_of_week = request.POST.get('day_of_week')
            time = request.POST.get('time')
            subject = request.POST.get('subject')
            room = request.POST.get('room', '')
            
            if day_of_week and time and subject:
                try:
                    Schedule.objects.create(
                        group=group,
                        day_of_week=int(day_of_week),
                        time=time,
                        subject=subject,
                        room=room
                    )
                except Exception as e:
                    pass
        
        elif action == 'delete':
            schedule_id = request.POST.get('schedule_id')
            Schedule.objects.filter(id=schedule_id, group=group).delete()
        
        return redirect('core:admin_schedule_group', group_id=group_id)
    
    return render(request, 'core/admin/schedule_group.html', {
        'group': group,
        'schedules': schedules,
        'day_choices': Schedule.DAY_CHOICES
    })


@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    return render(request, 'core/admin/panel.html')


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all()
    return render(request, 'core/admin/users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def admin_groups(request):
    groups = StudyGroup.objects.all()
    return render(request, 'core/admin/groups.html', {'groups': groups})


@login_required
@user_passes_test(is_admin)
def admin_group_detail(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)
    subjects = group.subjects.all()
    return render(request, 'core/admin/group_detail.html', {'group': group, 'subjects': subjects})


@login_required
@user_passes_test(is_admin)
def admin_subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    modules = subject.modules.all()
    return render(request, 'core/admin/subject_detail.html', {'subject': subject, 'modules': modules})


@login_required
@user_passes_test(is_admin)
def admin_module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    lectures = module.lectures.all()
    tests = module.tests.all()
    return render(request, 'core/admin/module_detail.html', {'module': module, 'lectures': lectures, 'tests': tests})


@login_required
@user_passes_test(is_admin)
def admin_test_detail(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()
    return render(request, 'core/admin/test_detail.html', {'test': test, 'questions': questions})


@login_required
@user_passes_test(is_admin)
def admin_journal(request):
    groups = StudyGroup.objects.all().order_by('name')
    return render(request, 'core/admin/journal_groups.html', {'groups': groups})


@login_required
@user_passes_test(is_admin)
def admin_journal_group_detail(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)
    subjects = group.subjects.all().order_by('name')
    return render(request, 'core/admin/journal_group_detail.html', {
        'group': group,
        'subjects': subjects
    })


@login_required
@user_passes_test(is_admin)
def admin_journal_subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Get all test attempts for modules in this subject
    attempts = TestAttempt.objects.filter(
        test__module__subject=subject
    ).select_related('user', 'test', 'test__module').order_by('-created')
    
    # Get all tests for this subject
    tests = Test.objects.filter(module__subject=subject).order_by('module__name', 'name').distinct()
    
    # Get all students who took tests in this subject
    students = User.objects.filter(
        testattempt__test__module__subject=subject,
        role='student'
    ).distinct().order_by('first_name', 'last_name')
    
    # Build matrix: student -> test -> best score
    matrix = {}
    for student in students:
        matrix[student.id] = {
            'student': student,
            'scores': {}
        }
        for test in tests:
            # Get best score for this student on this test
            best_attempt = TestAttempt.objects.filter(
                user=student,
                test=test
            ).order_by('-score').first()
            
            matrix[student.id]['scores'][test.id] = {
                'test': test,
                'score': best_attempt.score if best_attempt else None,
                'attempts': TestAttempt.objects.filter(user=student, test=test).count()
            }
    
    return render(request, 'core/admin/journal_subject_detail.html', {
        'subject': subject,
        'group': subject.group,
        'tests': tests,
        'matrix': matrix.values(),
        'attempts': attempts
    })


@login_required
def index(request):
    if request.user.role == 'admin':
        return render(request, 'core/admin_dashboard.html')
    # Student: show subjects of their group + schedule
    if request.user.study_group:
        from .models import Schedule
        subjects = request.user.study_group.subjects.all()
        schedule = Schedule.objects.filter(group=request.user.study_group).order_by('day_of_week', 'time')
        return render(request, 'core/student_dashboard.html', {
            'subjects': subjects,
            'schedule': schedule,
            'day_choices': Schedule.DAY_CHOICES
        })
    return render(request, 'core/student_dashboard.html', {'subjects': [], 'schedule': [], 'day_choices': []})


@login_required
def lectures_list(request):
    user = request.user
    if user.role == 'student' and user.study_group:
        lectures = Lecture.objects.filter(assigned_groups=user.study_group)
    else:
        lectures = Lecture.objects.all()
    return render(request, 'core/lectures_list.html', {'lectures': lectures})


@login_required
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    # Check permission for student
    if request.user.role == 'student' and request.user.study_group != subject.group:
        return render(request, 'core/subject_detail.html', {'error': 'Доступ запрещён'})
    modules = subject.modules.all()
    return render(request, 'core/subject_detail.html', {'subject': subject, 'modules': modules})


@login_required
def module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    lectures = module.lectures.all()
    tests = module.tests.all()
    return render(request, 'core/module_detail.html', {'module': module, 'lectures': lectures, 'tests': tests})


@login_required
def student_journal(request):
    # Get all test attempts for current student grouped by subject
    user = request.user
    if user.role != 'student':
        return render(request, 'core/student_journal.html', {'error': 'Доступ запрещён'})
    
    attempts = TestAttempt.objects.filter(user=user).select_related('test__module__subject').order_by('-created')
    
    # Group by subject with average score and max score
    subjects_data = {}
    for attempt in attempts:
        subject = attempt.test.module.subject
        if subject is None:  # Skip if subject is not set
            continue
        if subject.id not in subjects_data:
            subjects_data[subject.id] = {
                'subject': subject,
                'attempts': [],
                'total_score': 0,
                'max_score': 0,
                'count': 0
            }
        subjects_data[subject.id]['attempts'].append(attempt)
        subjects_data[subject.id]['total_score'] += attempt.score
        subjects_data[subject.id]['max_score'] = max(subjects_data[subject.id]['max_score'], attempt.score)
        subjects_data[subject.id]['count'] += 1
    
    # Calculate average for each subject
    for data in subjects_data.values():
        data['average'] = data['total_score'] / data['count'] if data['count'] > 0 else 0
    
    return render(request, 'core/student_journal.html', {'subjects_data': subjects_data.values()})


@login_required
def lecture_detail(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    if request.user.role == 'student' and request.user.study_group not in lecture.assigned_groups.all():
        return render(request, 'core/lecture_detail.html', {'error': 'Доступ запрещён'})

    content = None
    ext = lecture.file_ext
    file_url = lecture.file.url
    if ext == 'md':
        path = os.path.join(settings.MEDIA_ROOT, lecture.file.name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            content = md.markdown(text)
        except Exception:
            content = '<p>Не удалось загрузить Markdown.</p>'
    elif ext == 'docx' and mammoth:
        path = os.path.join(settings.MEDIA_ROOT, lecture.file.name)
        try:
            with open(path, 'rb') as f:
                res = mammoth.convert_to_html(f)
                content = res.value
        except Exception:
            content = '<p>Не удалось конвертировать DOCX.</p>'

    return render(request, 'core/lecture_detail.html', {'lecture': lecture, 'content': content, 'file_url': file_url})


@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    
    # Check if student exceeded attempt limit
    user_attempts = TestAttempt.objects.filter(user=request.user, test=test).count()
    if user_attempts >= test.attempts_limit:
        return render(request, 'core/take_test.html', {
            'test': test,
            'error': f'Вы исчерпали максимальное количество попыток ({test.attempts_limit}). Последний результат: {TestAttempt.objects.filter(user=request.user, test=test).latest("created").score:.1f}%'
        })
    
    if request.method == 'POST':
        total = 0
        correct = 0
        for q in test.questions.all():
            total += 1
            choice_id = request.POST.get(f'question_{q.id}')
            if choice_id:
                try:
                    c = Choice.objects.get(id=int(choice_id))
                    if c.correct:
                        correct += 1
                except Choice.DoesNotExist:
                    pass
        score = (correct / total) * 100 if total else 0
        TestAttempt.objects.create(user=request.user, test=test, score=score)
        
        # Check if this was last attempt
        remaining = test.attempts_limit - (user_attempts + 1)
        
        return render(request, 'core/take_result.html', {
            'score': score,
            'test': test,
            'attempts_left': remaining,
            'attempts_limit': test.attempts_limit
        })

    return render(request, 'core/take_test.html', {
        'test': test,
        'attempts_left': test.attempts_limit - user_attempts,
        'attempts_limit': test.attempts_limit
    })
