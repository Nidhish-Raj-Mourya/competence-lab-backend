from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.get_categories, name='categories'),
    path('tests/', views.get_tests, name='tests'),
    path('tests/<int:test_id>/', views.get_test_detail, name='test-detail'),
    path('tests/<int:test_id>/submit/', views.submit_test, name='submit-test'),
    path('results/<int:attempt_id>/', views.get_result, name='result'),
]