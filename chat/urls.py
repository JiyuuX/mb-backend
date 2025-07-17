from django.urls import path
from .views import ConversationListCreateView, MessageListCreateView, MarkConversationReadView

urlpatterns = [
    path('conversations/', ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:conversation_id>/messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('conversations/<int:conversation_id>/mark_read/', MarkConversationReadView.as_view(), name='conversation-mark-read'),
] 