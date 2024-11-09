from django.shortcuts import render, redirect
from inventory.models import CustomUser
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer,OrderSerializer
from .models import *
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
def pending_orders(request):
    pending_orders = Order.objects.filter(order_status="Pending")
    serialized_orders = OrderSerializer(pending_orders, many=True).data
    return Response(serialized_orders)

