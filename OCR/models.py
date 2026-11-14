from django.db import models

class ImageAnalysisResult(models.Model):
    image = models.ImageField(upload_to='images/')
    description = models.TextField()
    azure_response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.image.name} - {self.description}'