# serializers.py
from rest_framework import serializers
from inventory.models import CustomUser,Item,Symptom  # Adjust the import according to your project structure
from .models import Cart,Order,CartDetails
from inventory.serializers import MedImageSerializer,AddressSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','first_name', 'last_name', 'email', 'username', 'password', 'gender', 'user_type']
        extra_kwargs = {'password': {'write_only': True}}  # Ensure the password is write-only

    def create(self, validated_data):
        # Create a new user with the hashed password
        user = CustomUser(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            username=validated_data['username'],
            gender=validated_data['gender'],
            user_type=validated_data['user_type']
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartDetails
        fields = '__all__'

class OnlineItemSerializer(serializers.ModelSerializer):
    dosage_unit = serializers.CharField(write_only=True)  # Add dosage_unit field as write-only
    image = MedImageSerializer(read_only=True)  # Add the nested serializer for the image
    class Meta:
        model = Item
        fields = ['id','name', 'med_formula', 'category', 'company', 'dosage_strength', 'dosage_unit', 'form', 'qty_per_pack', 'price', 'packaging_unit', 'min_threshold_qty', 'max_threshold_qty', 'description', 'usage', 'precautions', 'item_status', 'qty_status','qty_sold','item_status','is_ordered','current_qty','image']

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
    
class FilteredDataSerializer(serializers.Serializer):
    address = AddressSerializer()
    cart_details = CartSerializer(many=True)
    rider = UserSerializer()    

class UniqueSymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = '_all_'   