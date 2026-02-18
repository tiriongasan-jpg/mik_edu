from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudyGroup, Subject, Module, Lecture, Test, Question, Choice, TestAttempt


class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra', {'fields': ('role', 'study_group')}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(StudyGroup)
admin.site.register(Subject)
admin.site.register(Module)
admin.site.register(Lecture)


class ChoiceInline(admin.TabularInline):
    model = Choice


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Test)
admin.site.register(TestAttempt)
