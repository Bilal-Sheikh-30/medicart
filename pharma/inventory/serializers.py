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
class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = '__all__'


class MedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedImage
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    dosage_unit = serializers.CharField(write_only=True)  # Add dosage_unit field as write-only
    class Meta:
        model = Item
        fields = ['name', 'med_formula', 'category', 'company', 'dosage_strength', 'dosage_unit', 'form', 'qty_per_pack', 'price', 'packaging_unit', 'min_threshold_qty', 'max_threshold_qty', 'description', 'usage', 'precautions', 'item_status', 'qty_status']

    def validate(self, data):
        # Combine dosage_strength and dosage_unit
        dosage_strength = data.get('dosage_strength')
        dosage_unit = data.pop('dosage_unit', None)  # Remove dosage_unit after getting its value

        if dosage_strength and dosage_unit:
            data['dosage_strength'] = f"{dosage_strength} {dosage_unit}"
        return data

    def create(self, validated_data):
        # Save the item with combined dosage_strength
        return super().create(validated_data)