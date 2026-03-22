from django.contrib import admin
from .models import Category, Test, TestSection, Question, TestAttempt, StudentAnswer


class TestSectionInline(admin.TabularInline):
    model = TestSection
    extra = 1
    fields = ['name', 'section_type', 'duration_minutes', 'total_marks', 'order']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 5
    # fields = ['order', 'question_type', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'marks']
    fields = ['order', 'section', 'question_type', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'marks']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'test_type', 'company_name', 'difficulty', 'duration_minutes', 'is_active']
    list_filter = ['test_type', 'difficulty', 'is_active']
    inlines = [TestSectionInline, QuestionInline]


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'student_email', 'test', 'score', 'percentage', 'passed', 'started_at']
    list_filter = ['test', 'passed']
    readonly_fields = ['started_at']