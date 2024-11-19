from django.db import models

class ImageUpload(models.Model):
    original_image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
