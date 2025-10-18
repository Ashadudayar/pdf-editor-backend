from rest_framework import serializers
from .models import PDFDocument

class PDFDocumentSerializer(serializers.ModelSerializer):
    original_file = serializers.SerializerMethodField()
    edited_file = serializers.SerializerMethodField()
    
    class Meta:
        model = PDFDocument
        fields = '__all__'
    
    def get_original_file(self, obj):
        request = self.context.get('request')
        if obj.original_file and request:
            return request.build_absolute_uri(obj.original_file.url)
        return None
    
    def get_edited_file(self, obj):
        request = self.context.get('request')
        if obj.edited_file and request:
            return request.build_absolute_uri(obj.edited_file.url)
        return None