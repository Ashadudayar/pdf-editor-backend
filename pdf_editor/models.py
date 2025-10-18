from django.db import models
import uuid

class PDFDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    original_file = models.FileField(upload_to='pdfs/original/')
    edited_file = models.FileField(upload_to='pdfs/edited/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title