from django.contrib import admin
from .models import PDFDocument

@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_size', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']
    readonly_fields = ['id', 'created_at']