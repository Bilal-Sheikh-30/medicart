from django.shortcuts import render
from inventory.models import CustomUser
from django.contrib.auth import login, authenticate
from django.urls import reverse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from inventory import models as invModels
from inventory import serializers as invSerializers
from django.db.models import Q

# Create your views here.

def homepage(request):
    return render(request, 'homepage.html')

@api_view(['POST'])
def loginFunction(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')

    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)  # Log the user in

        # Create a response object to handle redirection or success messages
        response_data = {
            'message': 'Login successful.',
            'user_type': user.user_type,
        }

        # Depending on user type, you can include redirect information if needed
        if user.user_type == 'user':
            response_data['redirect_url'] = reverse('homepage')
        elif user.user_type == 'warehouse':
            response_data['redirect_url'] = reverse('inventory:warehousepage')
        elif user.user_type == 'sales':
            response_data['redirect_url'] = reverse('inventory:salespage')
        elif user.user_type == 'rider':
            response_data['redirect_url'] = reverse('inventory:riderpage')
        else:
            response_data['redirect_url'] = reverse('homepage')

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid Credentials.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signupFunction(request):
    data = request.data
    serializer = UserSerializer(data=data)

    # Check if the user already exists
    if CustomUser.objects.filter(email=data.get('email')).exists():
        return Response({'error': 'Email already exists. Cannot register.'}, status=status.HTTP_400_BAD_REQUEST)
    elif CustomUser.objects.filter(username=data.get('username')).exists():
        return Response({'error': 'Username already exists. Cannot register.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate and save the new user
    if serializer.is_valid():
        user = serializer.save()  # Save the user
        login(request, user)  # Log the user in after registration
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def itemByCategory(request, catgId):
    items = invModels.Item.objects.filter(category = catgId, item_status = 'active').exclude(qty_status = 'finished')
    if items.exists():
        serializedItems = OnlineItemSerializer(items, many=True).data
        return Response(serializedItems, status=status.HTTP_200_OK)
    else:
        return Response('No items for this category', status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def getHotItems(request):
    hotItems = invModels.Item.objects.filter(item_status = 'active').exclude(Q(qty_status = 'finished') | Q(qty_sold = 0)).order_by('-qty_sold')
    if hotItems.exists():
        serializedHotItems = OnlineItemSerializer(hotItems, many=True).data
        return Response(serializedHotItems, status=status.HTTP_200_OK)
    else:
        return Response('Np hot items rightnow :(', status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def searchItems(request):
    queriedItem = request.data.get('search')
    
    if not queriedItem:
        return Response(
            {'detail': 'Search term is required.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    # search in item table with NAME
    searchResult_item = invModels.Item.objects.filter(name=queriedItem)
    
    # Search for formulas by name
    searchResult_formula = invModels.MedFormula.objects.filter(formula_name=queriedItem)

    items_from_formula = []
    if searchResult_formula.exists():
        formula = searchResult_formula.first()
        items_from_formula = invModels.Item.objects.filter(med_formula=formula)
    
    combined_items = searchResult_item.union(items_from_formula)

    serialized_items = invSerializers.ItemSerializer(combined_items, many=True).data

    if serialized_items:
        return Response(
            {
                'searchResult': serialized_items,
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'detail': 'No matching items or formulas found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )



