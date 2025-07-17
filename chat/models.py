from django.db import models
from django.conf import settings

class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Konuşma'
        verbose_name_plural = 'Konuşmalar'
        unique_together = ('id',)

    def __str__(self):
        return f"Konuşma: {' - '.join([user.username for user in self.participants.all()])}"

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField(blank=True, null=True)
    media = models.FileField(upload_to='chat_media/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mesaj'
        verbose_name_plural = 'Mesajlar'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.text[:30] if self.text else '[Medya]'}" 