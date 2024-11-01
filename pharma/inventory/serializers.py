from rest_framework import serializers
from .models import *

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedCategory
        fields = '__all__'

class MedFormulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedFormula
        fields = '__all__'
