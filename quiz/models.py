from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_questions = models.IntegerField()
    correct_questions = models.IntegerField()
    difficulty_level = models.IntegerField()
    quiz_date = models.DateTimeField(auto_now_add=True)
    completion_seconds = models.FloatField(null=True)


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    expression = models.CharField(max_length=100)
    correct_answer = models.IntegerField()
    difficulty_level = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user_answer = models.IntegerField(null=True, blank=True)  # Allow null
    is_correct = models.BooleanField(default=False)
    answer_date = models.DateTimeField(auto_now=True)
