from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .mit_chat_api import MITChatSendView
from .question_paper_api import (
    QuestionPaperExtractNotesView,
    QuestionPaperGenerateView,
    QuestionPaperImportToExamView,
)
from .views import AIAssistantViewSet, AIRequestHistoryView

router = DefaultRouter()
router.register('assistant', AIAssistantViewSet, basename='ai-assistant')

urlpatterns = [
    path('mit-chat/send/', MITChatSendView.as_view(), name='ai-mit-chat-send'),
    path('history/', AIRequestHistoryView.as_view(), name='ai-history'),
    path(
        'question-paper/generate/',
        QuestionPaperGenerateView.as_view(),
        name='ai-question-paper-generate',
    ),
    path(
        'question-paper/extract-notes/',
        QuestionPaperExtractNotesView.as_view(),
        name='ai-question-paper-extract-notes',
    ),
    path(
        'question-paper/import-to-exam/',
        QuestionPaperImportToExamView.as_view(),
        name='ai-question-paper-import-to-exam',
    ),
    path('', include(router.urls)),
]
