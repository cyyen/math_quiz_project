from datetime import datetime
import random
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
from django.forms import CharField
from django.shortcuts import render, redirect
from django.db.models import OuterRef, Subquery, Count, Q, F, CharField
from django.db.models.functions import Cast
from quiz.models import Quiz, Question, Answer
from quiz.serializers import QuizSerializer, QuestionSerializer, AnswerSerializer
from quiz.utils import get_difficulty_name, DIFFICULTY_LEVELS


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_queryset(self):
        return Quiz.objects.filter(user=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(user=self.request.user)


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answer.objects.filter(user=self.request.user)


@login_required
def new_quiz(request):
    if request.method == "POST":
        if "difficulty" in request.POST:
            # Start new quiz
            difficulty = int(request.POST["difficulty"])
            total_questions = int(request.POST["total_questions"])
            quiz = Quiz.objects.create(
                user=request.user,
                total_questions=total_questions,
                correct_questions=0,
                difficulty_level=difficulty,
                completion_seconds=0.0,
            )

            # Generate questions
            for _ in range(total_questions):
                num1 = random.randint(0, difficulty)
                num2 = random.randint(0, difficulty - num1)
                expression = f"{num1}+{num2}"

                Question.objects.create(
                    user=request.user,
                    quiz=quiz,
                    expression=expression,
                    correct_answer=num1 + num2,
                    difficulty_level=difficulty,
                )

            return redirect("quiz_question", quiz_id=quiz.id, question_number=1)

    return render(
        request, "quiz/new_quiz.html", {"difficulty_levels": DIFFICULTY_LEVELS}
    )


@login_required
def quiz_question(request, quiz_id, question_number):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    current_question = questions[question_number - 1]

    if request.method == "POST":
        answer = int(request.POST.get("answer"))
        Answer.objects.create(
            user=request.user,
            question=current_question,
            quiz=quiz,
            user_answer=answer,
            is_correct=answer == current_question.correct_answer,
            answer_date=datetime.now(),
        )
        quiz.completion_seconds = float(request.POST.get("completion_seconds"))
        if answer == current_question.correct_answer:
            quiz.correct_questions += 1
            quiz.save()

        if question_number >= quiz.total_questions:
            quiz.completion_seconds = float(request.POST.get("completion_seconds"))
            quiz.save()
            return redirect("score_list")

        return redirect(
            "quiz_question", quiz_id=quiz_id, question_number=question_number + 1
        )

    return render(
        request,
        "quiz/quiz_question.html",
        {
            "quiz": quiz,
            "question": current_question,
            "question_number": question_number,
            "progress": (question_number / quiz.total_questions) * 100,
        },
    )


@login_required
def score_list(request):
    latest_retries = Answer.objects.filter(question=OuterRef("question")).order_by(
        "-answer_date"
    )
    scores = (
        Quiz.objects.filter(user=request.user)
        .annotate(
            wrong_count=F("total_questions")
            - Count(
                "question",
                filter=Q(
                    answer__in=Subquery(latest_retries.values("id")[:1]),
                    answer__is_correct=True,
                ),
            ),
            difficulty_str=Cast("difficulty_level", output_field=CharField()),
        )
        .order_by("-quiz_date")
    )
    for score in scores:
        score.difficulty_name = get_difficulty_name(score.difficulty_str)
        score.score_percentage = 100 * score.correct_questions / score.total_questions
    return render(request, "quiz/score_list.html", {"scores": scores})


@login_required
def retry_list(request):
    # Get quizzes that have at least one wrong answer
    latest_retries = Answer.objects.filter(question=OuterRef("question")).order_by(
        "-answer_date"
    )
    quizzes = (
        Quiz.objects.filter(user=request.user)
        .annotate(
            wrong_count=F("total_questions")
            - Count(
                "question",
                filter=Q(
                        answer__in=Subquery(latest_retries.values("id")[:1]),
                        answer__is_correct=True,
                ),
            ),
            score_percentage=100.0 * F("correct_questions") / F("total_questions"),
            difficulty_str=Cast("difficulty_level", output_field=CharField()),
        )
        .filter(wrong_count__gt=0)
        .distinct()
        .order_by("-quiz_date")
    )
    for quizz in quizzes:
        quizz.difficulty_name = get_difficulty_name(quizz.difficulty_str)

    return render(request, "quiz/retry_list.html", {"quizzes": quizzes})


@login_required
def retry_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    quiz.difficulty_name = get_difficulty_name(quiz.difficulty_level)
    latest_retries = Answer.objects.filter(quiz_id=quiz_id).order_by("-answer_date")

    wrong_questions = (
        Question.objects.filter(quiz=quiz)
        .annotate(
            latest_retry=Subquery(
                latest_retries.filter(question_id=OuterRef("id")).values("is_correct")[
                    :1
                ]
            ),
            user_answer=Subquery(
                latest_retries.filter(question_id=OuterRef("id")).values("user_answer")[
                    :1
                ]
            ),
        )
        .filter(Q(latest_retry__isnull=True) | Q(latest_retry=False))
        .order_by("id")
    )

    if request.method == "POST":
        question_id = request.POST.get("question_id")
        answer = int(request.POST.get("answer"))
        question = Question.objects.get(id=question_id)

        Answer.objects.create(
            user=request.user,
            question=question,
            quiz=question.quiz,
            user_answer=answer,
            is_correct=answer == question.correct_answer,
            answer_date=datetime.now(),
        )

    # Get first wrong question that hasn't been answered correctly
    current_question = wrong_questions.first()
    total_questions = wrong_questions.count()
    current_index = (
        list(wrong_questions).index(current_question) if current_question else 0
    )
    progress = (current_index / total_questions * 100) if total_questions > 0 else 100

    return render(
        request,
        "quiz/retry_quiz.html",
        {
            "quiz": quiz,
            "current_question": current_question,
            "current_index": current_index,
            "total_questions": total_questions,
            "progress": progress,
        },
    )
