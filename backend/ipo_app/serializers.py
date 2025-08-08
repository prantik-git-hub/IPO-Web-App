from rest_framework import serializers
from .models import Company, IPO, Document

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class IPOSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    documents = DocumentSerializer(many=True, read_only=True)  # ✅ related_name='documents' in model

    class Meta:
        model = IPO
        fields = '__all__'
