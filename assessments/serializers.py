from rest_framework import serializers
from .models import Category, Test, TestSection, Question, TestAttempt, StudentAnswer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'order', 'question_type', 'text',
            'option_a', 'option_b', 'option_c', 'option_d',
            'marks', 'section'
        ]
        # correct_option yahan nahi — cheat rokne ke liye!


class TestSectionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = TestSection
        fields = [
            'id', 'name', 'section_type',
            'duration_minutes', 'total_marks',
            'order', 'questions'
        ]


class TestListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = [
            'id', 'title', 'description', 'test_type',
            'company_name', 'difficulty', 'duration_minutes',
            'total_marks', 'pass_marks', 'category_name',
            'question_count', 'is_featured'
        ]

    def get_question_count(self, obj):
        return obj.questions.count()


class TestDetailSerializer(serializers.ModelSerializer):
    sections = TestSectionSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    class Meta:
        model = Test
        fields = [
            'id', 'title', 'description', 'test_type',
            'company_name', 'difficulty', 'duration_minutes',
            'total_marks', 'pass_marks', 'category_name',
            'sections', 'questions'
        ]


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['question', 'selected_option', 'submitted_code', 'coding_language']


class TestSubmitSerializer(serializers.Serializer):
    student_name = serializers.CharField(max_length=100)
    student_email = serializers.EmailField()
    student_roll = serializers.CharField(max_length=50, required=False, allow_blank=True)
    institute_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    answers = StudentAnswerSerializer(many=True)
    time_taken_seconds = serializers.IntegerField()


class TestAttemptSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    test_type = serializers.CharField(source='test.test_type', read_only=True)

    class Meta:
        model = TestAttempt
        fields = [
            'id', 'student_name', 'student_email',
            'test_title', 'test_type', 'score',
            'total_marks', 'percentage', 'passed',
            'correct_answers', 'wrong_answers', 'skipped',
            'time_taken_seconds', 'started_at', 'completed_at',
            'section_scores'
        ]