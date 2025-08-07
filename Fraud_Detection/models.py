from django.db import models
from django.conf import settings

class Prediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prediction_data = models.JSONField()  # Store results dictionary
    created_at = models.DateTimeField(auto_now_add=True)
    graph_file_name = models.CharField(max_length=255, blank=True, null=True)  # store graph file name
    def __str__(self):
        return f"Prediction by {self.user.username} on {self.created_at}"

