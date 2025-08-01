from django.urls import path
from .views import ConversationListCreateView, MessageListCreateView, MarkConversationReadView, UpdateMessageStatusView, MarkMessagesAsReadView, MarkMyMessagesAsReadView

urlpatterns = [
    path('conversations/', ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:conversation_id>/messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('conversations/<int:conversation_id>/mark_read/', MarkConversationReadView.as_view(), name='conversation-mark-read'),
    path('conversations/<int:conversation_id>/mark_messages_read/', MarkMessagesAsReadView.as_view(), name='mark-messages-read'),
    path('conversations/<int:conversation_id>/mark_my_messages_read/', MarkMyMessagesAsReadView.as_view(), name='mark-my-messages-read'),
    path('messages/<int:message_id>/status/', UpdateMessageStatusView.as_view(), name='message-status-update'),
] 