"""MIT AI Chat API — isolated from AIAssistantViewSet (ChatGPT-style for all roles)."""
import logging

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AIRequest, AIRequestType
from .mit_chat_service import mit_chat_completion

logger = logging.getLogger(__name__)


class MITChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['user', 'assistant'])
    content = serializers.CharField(max_length=12000)


class MITChatSendSerializer(serializers.Serializer):
    messages = serializers.ListField(
        child=MITChatMessageSerializer(),
        min_length=1,
        max_length=30,
        help_text='Conversation history; last item must be role=user.',
    )


class MITChatSendView(APIView):
    """POST /api/v1/ai/mit-chat/send/ — ChatGPT-style message (all authenticated roles)."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(request=MITChatSendSerializer)
    def post(self, request):
        serializer = MITChatSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = serializer.validated_data['messages']
        last = messages[-1]
        if last['role'] != 'user':
            return Response(
                {'detail': 'The last message must be from the user.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = mit_chat_completion(
                messages=messages,
                user_role=getattr(request.user, 'role', 'student'),
            )
            AIRequest.objects.create(
                user=request.user,
                request_type=AIRequestType.CHAT,
                prompt=last['content'][:2000],
                response=result.content,
                is_success=True,
                latency_ms=result.latency_ms,
                metadata={'feature': 'mit_chat', 'role': request.user.role},
            )
            return Response({
                'message': {
                    'role': 'assistant',
                    'content': result.content,
                },
                'latency_ms': result.latency_ms,
            })
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except RuntimeError as exc:
            logger.exception('MIT Chat Databricks error')
            AIRequest.objects.create(
                user=request.user,
                request_type=AIRequestType.CHAT,
                prompt=last['content'][:2000],
                is_success=False,
                error=str(exc),
                metadata={'feature': 'mit_chat', 'role': request.user.role},
            )
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as exc:
            logger.exception('MIT Chat unexpected error')
            return Response({'detail': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
