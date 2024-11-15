"""
URL configuration for math_quiz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from quiz import views
from django.contrib.auth import views as auth_views
schema_view = get_schema_view(
    openapi.Info(
        title="Math Quiz API",
        default_version="v1",
        description="API for Math Quiz application",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("quiz.urls")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0)),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0)),
    path("", views.new_quiz, name="new_quiz"),
    path("scores/", views.score_list, name="score_list"),
    path("retry/", views.retry_list, name="retry_list"),
    path("retry/<int:quiz_id>/", views.retry_quiz, name="retry_quiz"),
    path(
        "quiz/<int:quiz_id>/question/<int:question_number>/",
        views.quiz_question,
        name="quiz_question",
    ),

]
