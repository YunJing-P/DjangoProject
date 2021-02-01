from django.db import models


class Feedback(models.Model):
    feedback_text = models.TextField()
    chat_id = models.CharField(max_length=200)
    user_id = models.CharField(max_length=200)
    is_done = models.IntegerField(default=0)
    c_time = models.DateTimeField(auto_now_add=True)
    m_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.feedback_text


