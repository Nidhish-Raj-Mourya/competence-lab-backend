from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Test(models.Model):

    TEST_TYPE_CHOICES = [
        ('aptitude', 'Aptitude Practice'),
        ('coding', 'Coding Test'),
        ('mock', 'Company Mock Test'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    test_type = models.CharField(
        max_length=20,
        choices=TEST_TYPE_CHOICES,
        default='aptitude'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='tests'
    )

    # Company mock ke liye
    company_name = models.CharField(
        max_length=100,
        blank=True
    )
    # TCS, Infosys, Wipro, Amazon etc

    # Test settings
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    duration_minutes = models.IntegerField(default=30)
    total_marks = models.IntegerField(default=100)
    pass_marks = models.IntegerField(default=40)

    # Display settings
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.company_name:
            return f"{self.company_name} - {self.title}"
        return self.title

    class Meta:
        ordering = ['order', '-created_at']


class TestSection(models.Model):
    """
    Company mock mein multiple sections hote hain
    TCS Mock → Section 1: Aptitude, Section 2: Coding
    """
    SECTION_TYPE_CHOICES = [
        ('aptitude', 'Aptitude'),
        ('reasoning', 'Reasoning'),
        ('verbal', 'Verbal'),
        ('coding', 'Coding'),
        ('technical', 'Technical MCQ'),
    ]

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    name = models.CharField(max_length=100)
    section_type = models.CharField(
        max_length=20,
        choices=SECTION_TYPE_CHOICES
    )
    duration_minutes = models.IntegerField(default=20)
    total_marks = models.IntegerField(default=30)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.test.title} → {self.name}"

    class Meta:
        ordering = ['order']


class Question(models.Model):
    OPTION_CHOICES = [
        ('A', 'A'), ('B', 'B'),
        ('C', 'C'), ('D', 'D')
    ]

    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice'),
        ('coding', 'Coding Problem'),
    ]

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    section = models.ForeignKey(
        TestSection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions'
    )

    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default='mcq'
    )

    # MCQ fields
    text = models.TextField()
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_option = models.CharField(
        max_length=1,
        choices=OPTION_CHOICES,
        blank=True
    )
    explanation = models.TextField(blank=True)

    # Coding fields
    sample_input = models.TextField(blank=True)
    sample_output = models.TextField(blank=True)
    test_cases = models.JSONField(default=list, blank=True)
    # [{"input": "...", "output": "...", "is_public": true}]

    marks = models.IntegerField(default=1)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"

    class Meta:
        ordering = ['order']


class TestAttempt(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    # Student info
    student_name = models.CharField(max_length=100)
    student_email = models.EmailField()
    student_roll = models.CharField(max_length=50, blank=True)
    institute_name = models.CharField(max_length=200, blank=True)

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='attempts'
    )

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.IntegerField(default=0)

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ongoing'
    )

    # Results
    score = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    skipped = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)

    # Section wise score (JSON)
    section_scores = models.JSONField(default=dict)
    # {"Aptitude": 25, "Reasoning": 18, "Coding": 20}

    def __str__(self):
        return f"{self.student_name} → {self.test.title} → {self.percentage}%"

    class Meta:
        ordering = ['-started_at']


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    # MCQ answer
    selected_option = models.CharField(
        max_length=1,
        blank=True
    )
    # Coding answer
    submitted_code = models.TextField(blank=True)
    coding_language = models.CharField(
        max_length=20,
        blank=True
    )

    is_correct = models.BooleanField(default=False)
    marks_obtained = models.IntegerField(default=0)
    time_spent_seconds = models.IntegerField(default=0)

    def __str__(self):
        return f"Q{self.question.order} → {self.selected_option}"