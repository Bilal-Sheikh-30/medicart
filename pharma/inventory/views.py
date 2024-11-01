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
    response_data = {'message':''}
    data = request.data
    serialized_formula = MedFormulaSerializer(data=data)
    if MedFormula.objects.filter(formula_name=data.get('formula_name')).exists():
        response_data['message'] = 'Formula already exists'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    elif serialized_formula.is_valid():
        new_formula = MedFormula(formula_name=data.get('formula_name'), category_id= data.get('category_id'))
        new_formula.save()
        response_data['message'] = 'Formula added.'
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized_formula.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def editformula(request, formula_id):
    response_data = {'message':''}
    formula = get_object_or_404(MedFormula, id=formula_id)
    data = request.data
    new_formula_name = data.get('formula_name')
    new_category_id = data.get('category_id')

    # Check if a category with the new name already exists (excluding the current category)
    if MedFormula.objects.filter(formula_name=new_formula_name).exclude(id=formula_id).exists():
        response_data['message'] = 'Formula name already exists!' 
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # Update and save the category
    formula.formula_name = new_formula_name
    formula.category_id = new_category_id
    formula.save()
    response_data['message'] = 'Formula updated.'
    return Response(response_data, status=status.HTTP_200_OK)

def allitems(request):
    items = Item.objects.all()
    return render(request,'allitems.html',{'items':items})

def sales(request):
    return render(request,'inv_layout.html')

def rider(request):
    return render(request,'inv_layout.html')