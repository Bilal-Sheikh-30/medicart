from django.shortcuts import render
from .models import *
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

# Create your views here.

def warehouse(request):
    return render(request,'warehouse_landing.html')

@api_view(['GET'])
def allcompanies(request):
    companies = Company.objects.all()
    serialized_companies = CompanySerializer(companies, many=True).data
    return Response(serialized_companies)

@api_view(['POST'])
def addcompany(request):
    response_data = {'message':''}
    data = request.data
    serialized_company = CompanySerializer(data=data)
    if Company.objects.filter(name=data.get('name')).exists():
        response_data['message'] = 'Company already exists'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    elif serialized_company.is_valid():
        serialized_company.save()
        response_data['message'] = 'Company added.'
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized_company.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def viewcategory(request):
    categories = MedCategory.objects.all()
    serialized_categories = CategorySerializer(categories, many=True).data
    return Response(serialized_categories)

@api_view(['POST'])
def addcategory(request):
    response_data = {'message':''}
    data = request.data
    serialized_category = CategorySerializer(data=data)
    if MedCategory.objects.filter(category_name=data.get('category_name')).exists():
        response_data['message'] = 'Category already exists'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    elif serialized_category.is_valid():
        serialized_category.save()
        response_data['message'] = 'Category added.'
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized_category.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def edit_category(request, category_id):
    response_data = {'message':''}
    category = get_object_or_404(MedCategory, id=category_id)
    data = request.data
    new_category_name = data.get('category_name')

    # Check if a category with the new name already exists (excluding the current category)
    if MedCategory.objects.filter(category_name=new_category_name).exclude(id=category_id).exists():
        response_data['message'] = 'Category name already exists!' 
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # Update and save the category
    category.category_name = new_category_name
    category.save()
    response_data['message'] = 'Category updated successfully.'
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def viewformulae(request):
    formulae = MedFormula.objects.all()
    serialized_formulae = MedFormulaSerializer(formulae, many=True).data
    return Response(serialized_formulae)


@api_view(['POST'])
def addformula(request):
    response_data = {'message': ''}
    data = request.data
    formula_name = data.get('formula_name')
    category_id = data.get('category_id')
    symptom_text = data.get('symptom')

    # Validate formula data
    serialized_formula = MedFormulaSerializer(data={'formula_name': formula_name, 'category_id': category_id})
    
    # Check if the formula already exists
    if MedFormula.objects.filter(formula_name=formula_name).exists():
        response_data['message'] = 'Formula already exists'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # If valid, save the formula
    elif serialized_formula.is_valid():
        new_formula = MedFormula(formula_name=formula_name, category_id=category_id)
        new_formula.save()
        
        # Now add the symptom with new_formula as the FK
        new_formula = MedFormula.objects.get(formula_name=formula_name)
        symptom_data = {'med_formula': new_formula.id, 'symptom': symptom_text}  # assuming `formula` is the FK in Symptom
        serialized_symptom = SymptomSerializer(data=symptom_data)
        
        if serialized_symptom.is_valid():
            serialized_symptom.save()
            response_data['message'] = 'Formula and symptom added successfully.'
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            # If the symptom data is invalid, delete the formula we just added to keep data consistent
            new_formula.delete()
            return Response(serialized_symptom.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serialized_formula.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def editformula(request, formula_id):
    response_data = {'message':''}
    formula = get_object_or_404(MedFormula, id=formula_id)
    old_symptom = get_object_or_404(Symptom, med_formula_id=formula)
    data = request.data
    new_formula_name = data.get('formula_name')
    new_category_id = data.get('category_id')
    new_symptom = data.get('symptom')

    # Check if a category with the new name already exists (excluding the current category)
    if MedFormula.objects.filter(formula_name=new_formula_name).exclude(id=formula_id).exists():
        response_data['message'] = 'Formula name already exists!' 
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # Update and save the category
    formula.formula_name = new_formula_name
    formula.category_id = new_category_id
    formula.save()
    old_symptom.symptom = new_symptom
    old_symptom.save()
    response_data['message'] = 'Formula updated.'
    return Response(response_data, status=status.HTTP_200_OK)

# tameez k sath items categorize kr k send krna hay
@api_view(['GET'])
def allitems(request):
    items = Item.objects.all()
    med_images = MedImage.objects.all()

    serialized_items = ItemSerializer(items, many=True).data
    serialized_images = MedImageSerializer(med_images,many=True).data

    data = {
        "items" : serialized_items,
        "images" : serialized_images
    }
    return Response(data)


@api_view(['POST'])
def add_item(request):
    response_data = {'message': ''}
    data = request.data

    # Extract item details, including the dosage_unit separately
    item_data = {
        'name': data.get('name'),
        'med_formula': data.get('med_formula'),
        'category': data.get('category'),
        'company': data.get('company'),
        'dosage_strength': data.get('dosage_strength'),  # e.g., "500"
        'dosage_unit': data.get('dosage_unit'),  # e.g., "mg"
        'form': data.get('form'),
        'qty_per_pack': data.get('qty_per_pack'),
        'price': data.get('price'),
        'packaging_unit': data.get('packaging_unit'),
        'min_threshold_qty': data.get('min_threshold_qty'),
        'max_threshold_qty': data.get('max_threshold_qty'),
        'description': data.get('description'),
        'usage': data.get('usage'),
        'precautions': data.get('precautions'),
        'item_status': data.get('item_status', 'active'),
        'qty_status': 'insufficient',
    }

    # Serialize and validate item data
    item_serializer = ItemSerializer(data=item_data)

    # Check if an item with the same name and dosage strength already exists
    if Item.objects.filter(name=item_data['name'], dosage_strength=f"{item_data['dosage_strength']} {item_data['dosage_unit']}").exists():
        response_data['message'] = 'Item with the same name and dosage strength already exists'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # Save the item if data is valid
    elif item_serializer.is_valid():
        item = item_serializer.save()

        # Handle the image if provided
        if 'image' in request.FILES:
            image_data = {'item': item.id, 'image': request.FILES['image']}
            image_serializer = MedImageSerializer(data=image_data)
            if image_serializer.is_valid():
                image_serializer.save()
                response_data['message'] = 'Item and image added successfully.'
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                # Delete the item if image data is invalid to maintain consistency
                item.delete()
                return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response_data['message'] = 'Item added successfully, no image provided.'
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def edit_item(request, item_id):
    response_data = {'message': ''}

    try:
        # Fetch the item to be updated
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response({'message': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    # Extract updated item data from the request
    updated_data = {
        'name': request.data.get('name', item.name),
        'med_formula': request.data.get('med_formula', item.med_formula),
        'category': request.data.get('category', item.category),
        'company': request.data.get('company', item.company),
        'dosage_strength': request.data.get('dosage_strength', item.dosage_strength),
        'dosage_unit': request.data.get('dosage_unit'),  # Expected as separate input for combination
        'form': request.data.get('form', item.form),
        'qty_per_pack': request.data.get('qty_per_pack', item.qty_per_pack),
        'price': request.data.get('price', item.price),
        'packaging_unit': request.data.get('packaging_unit', item.packaging_unit),
        'min_threshold_qty': request.data.get('min_threshold_qty', item.min_threshold_qty),
        'max_threshold_qty': request.data.get('max_threshold_qty', item.max_threshold_qty),
        'description': request.data.get('description', item.description),
        'usage': request.data.get('usage', item.usage),
        'precautions': request.data.get('precautions', item.precautions),
        'item_status': request.data.get('item_status', item.item_status),
        'qty_status': request.data.get('qty_status', item.qty_status),
    }

    # Combine dosage strength and unit if both are provided
    dosage_unit = updated_data.pop('dosage_unit', None)
    if dosage_unit:
        updated_data['dosage_strength'] = f"{updated_data['dosage_strength']} {dosage_unit}"

    # Serialize and validate the updated data
    item_serializer = ItemSerializer(item, data=updated_data, partial=True)

    # Validate and update item
    if item_serializer.is_valid():
        item_serializer.save()

        # Handle image if provided
        if 'image' in request.FILES:
            # If item already has an image, update it; otherwise, add new image
            if hasattr(item, 'image'):
                item.image.image = request.FILES['image']
                item.image.save()
            else:
                image_data = {'item': item.id, 'image': request.FILES['image']}
                image_serializer = MedImageSerializer(data=image_data)
                if image_serializer.is_valid():
                    image_serializer.save()
                else:
                    return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response_data['message'] = 'Item updated successfully.'
        return Response(response_data, status=status.HTTP_200_OK)

    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def sales(request):
    return render(request,'inv_layout.html')

def rider(request):
    return render(request,'inv_layout.html')