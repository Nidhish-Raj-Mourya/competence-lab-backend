from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import Category, Test, Question, TestAttempt, StudentAnswer
from .serializers import (
    CategorySerializer, TestListSerializer,
    TestDetailSerializer, TestSubmitSerializer,
    TestAttemptSerializer
)


@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_tests(request):
    test_type = request.query_params.get('type', None)
    tests = Test.objects.filter(is_active=True)
    if test_type:
        tests = tests.filter(test_type=test_type)
    serializer = TestListSerializer(tests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_test_detail(request, test_id):
    try:
        test = Test.objects.get(id=test_id, is_active=True)
    except Test.DoesNotExist:
        return Response(
            {'error': 'Test not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = TestDetailSerializer(test)
    return Response(serializer.data)


@api_view(['POST'])
def submit_test(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
    except Test.DoesNotExist:
        return Response(
            {'error': 'Test not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = TestSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    data = serializer.validated_data

    # Attempt create karo
    attempt = TestAttempt.objects.create(
        student_name=data['student_name'],
        student_email=data['student_email'],
        student_roll=data.get('student_roll', ''),
        institute_name=data.get('institute_name', ''),
        test=test,
        status='completed',
        completed_at=timezone.now(),
        time_taken_seconds=data['time_taken_seconds'],
        total_marks=test.total_marks,
        total_questions=test.questions.count(),
    )

    # Answers evaluate karo
    score = 0
    correct = 0
    wrong = 0
    skipped = 0

    for answer_data in data['answers']:
        question = answer_data['question']
        selected = answer_data.get('selected_option', '')

        is_correct = False
        marks_obtained = 0

        if selected == '':
            skipped += 1
        elif selected == question.correct_option:
            is_correct = True
            marks_obtained = question.marks
            score += question.marks
            correct += 1
        else:
            wrong += 1

        StudentAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_option=selected,
            is_correct=is_correct,
            marks_obtained=marks_obtained
        )

    # Results update karo
    percentage = (score / test.total_marks * 100) if test.total_marks > 0 else 0
    attempt.score = score
    attempt.correct_answers = correct
    attempt.wrong_answers = wrong
    attempt.skipped = skipped
    attempt.percentage = round(percentage, 2)
    attempt.passed = percentage >= test.pass_marks
    attempt.save()

    return Response({
        'attempt_id': attempt.id,
        'score': score,
        'total_marks': test.total_marks,
        'percentage': round(percentage, 2),
        'passed': attempt.passed,
        'correct': correct,
        'wrong': wrong,
        'skipped': skipped,
    })


@api_view(['GET'])
def get_result(request, attempt_id):
    try:
        attempt = TestAttempt.objects.get(id=attempt_id)
    except TestAttempt.DoesNotExist:
        return Response(
            {'error': 'Result not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = TestAttemptSerializer(attempt)
    return Response(serializer.data)