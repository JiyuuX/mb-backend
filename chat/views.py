from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from users.models import CustomUser
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def post(self, request, *args, **kwargs):
        other_user_id = request.data.get('user_id')
        if not other_user_id:
            return Response({'error': 'user_id gerekli.'}, status=400)
        try:
            other_user = CustomUser.objects.get(id=other_user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Kullanıcı bulunamadı.'}, status=404)
        # Aynı iki kişi arasında birden fazla konuşma olmasın
        conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, other_user)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=201)

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if self.request.user not in conversation.participants.all():
            return Message.objects.none()
        return conversation.messages.all()

    def perform_create(self, serializer):
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if self.request.user not in conversation.participants.all():
            raise PermissionError('Bu konuşmaya mesaj gönderemezsiniz.')
        print(f"Gelen veri: {self.request.data}")  # Debug için
        serializer.save(sender=self.request.user, conversation=conversation)

class MarkConversationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in conversation.participants.all():
            return Response({'error': 'Bu konuşmaya erişiminiz yok.'}, status=403)
        # Sadece başkasının gönderdiği ve okunmamış mesajları okundu yap
        updated = conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        return Response({'success': True, 'marked_read': updated})
