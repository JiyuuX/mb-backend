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

from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if self.request.user not in conversation.participants.all():
            return Message.objects.none()
        # Mesajları tarih sırasına göre sırala (en eski önce)
        return conversation.messages.all().order_by('created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Sayfa numarasını al
        page = request.query_params.get('page', 1)
        page_size = int(request.query_params.get('page_size', 20))
        
        try:
            page = int(page)
        except ValueError:
            page = 1
        
        # Toplam mesaj sayısını al
        total_messages = queryset.count()
        
        # Pagination hesaplamaları
        if page == 1:
            # İlk sayfa: En son mesajları göster (WhatsApp gibi)
            start_index = max(0, total_messages - page_size)
            messages = list(queryset[start_index:])
        else:
            # Eski mesajları yükle (scroll up için)
            # Sayfa 2: 0'dan (total - 2*page_size)'a kadar
            # Sayfa 3: 0'dan (total - 3*page_size)'a kadar
            start_index = 0
            end_index = max(0, total_messages - ((page - 1) * page_size))
            messages = list(queryset[start_index:end_index])
        
        serializer = self.get_serializer(messages, many=True)
        
        # Pagination bilgilerini hazırla
        has_next = end_index > page_size if page > 1 else total_messages > page_size
        has_previous = page > 1
        
        return Response({
            'count': total_messages,
            'next': f"?page={page + 1}" if has_next else None,
            'previous': f"?page={page - 1}" if has_previous else None,
            'results': serializer.data
        })

    def perform_create(self, serializer):
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if self.request.user not in conversation.participants.all():
            raise PermissionError('Bu konuşmaya mesaj gönderemezsiniz.')
        print(f"Gelen veri: {self.request.data}")
        message = serializer.save(sender=self.request.user, conversation=conversation, status='sent')
        print(f"Mesaj oluşturuldu: {message.id} - {message.text}")
        
        return message

class MarkConversationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in conversation.participants.all():
            return Response({'error': 'Bu konuşmaya erişiminiz yok.'}, status=403)
        # Sadece başkasının gönderdiği ve okunmamış mesajları okundu yap
        updated = conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True, status='read')
        return Response({'success': True, 'marked_read': updated})

class UpdateMessageStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if request.user not in message.conversation.participants.all():
                return Response({'error': 'Bu mesaja erişiminiz yok.'}, status=403)
            
            new_status = request.data.get('status')
            if new_status not in ['sent', 'delivered', 'read', 'failed']:
                return Response({'error': 'Geçersiz durum.'}, status=400)
            
            message.status = new_status
            message.save()
            
            return Response({'success': True, 'status': new_status})
        except Message.DoesNotExist:
            return Response({'error': 'Mesaj bulunamadı.'}, status=404)

class MarkMessagesAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in conversation.participants.all():
            return Response({'error': 'Bu konuşmaya erişiminiz yok.'}, status=403)
        
        # Sadece karşı tarafın gönderdiği mesajları 'read' yap
        read_count = conversation.messages.filter(
            status__in=['sent', 'delivered'],
            sender__in=conversation.participants.exclude(id=request.user.id)
        ).update(status='read', is_read=True)
        
        print(f"Marked {read_count} messages as read for user {request.user.username} in conversation {conversation_id}")
        
        return Response({
            'success': True, 
            'marked_read': read_count,
            'conversation_id': conversation_id
        })

class MarkMyMessagesAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in conversation.participants.all():
            return Response({'error': 'Bu konuşmaya erişiminiz yok.'}, status=403)
        
        # Kendi mesajlarımızın karşı taraf tarafından okunduğunu işaretle
        my_messages_read = conversation.messages.filter(
            sender=request.user,
            status='sent'
        ).update(status='read')
        
        print(f"Marked {my_messages_read} of my messages as read by others")
        
        return Response({
            'success': True, 
            'my_messages_read': my_messages_read
        })
