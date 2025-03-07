from django.shortcuts import render
from inventory.models import CustomUser
from django.contrib.auth import login, authenticate
from django.urls import reverse
import base64
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
        };

        # Depending on user type, you can include redirect information if needed
        if user.user_type == 'user':
            response_data['redirect_url'] = reverse('homepage')
        elif user.user_type == 'warehouse':
            response_data['redirect_url'] = reverse('inventory:warehousepage')
        elif user.user_type == 'sales':
            response_data['redirect_url'] = reverse('inventory:salespage')
        # elif user.user_type == 'rider':
        #     response_data['redirect_url'] = reverse('inventory:riderpage')
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
    
    # Search for items by name
    searchResult_item = invModels.Item.objects.filter(name=queriedItem)
    
    # Search for formulas by name
    searchResult_formula = invModels.MedFormula.objects.filter(formula_name=queriedItem)

    if searchResult_formula.exists():
        formula = searchResult_formula.first()
        items_from_formula = invModels.Item.objects.filter(med_formula=formula)
    else:
        items_from_formula = invModels.Item.objects.none()  # Empty QuerySet

    # Combine the results using union
    combined_items = searchResult_item.union(items_from_formula)

    # Serialize the combined results
    serialized_items = OnlineItemSerializer(combined_items, many=True).data

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



@api_view(['GET'])
def getqr(request):
    try:
        qr = invModels.QRCode.objects.all()
    except:
        return Response('Failed to retrieve QR :(', status=status.HTTP_404_NOT_FOUND)
    else:
        serializedQr = invSerializers.QRCodeSerializer(qr, many=True).data
        return Response(serializedQr, status=status.HTTP_302_FOUND)
    
@api_view(['GET'])
def getOrderHistory(request):
    carts = Cart.objects.filter(userID=request.user)
    cart_ids = carts.values_list('id', flat=True)
    orders = Order.objects.filter(cartId__in=cart_ids)

    orders = OrderSerializer(orders, many=True).data
    return Response(orders)    

@api_view(['GET'])
def getFilteredOrderDetails(request, cartId, addressId, riderId):

    if not (cartId and addressId and riderId):
        return Response({"error": "cartId, addressId, and riderId are required parameters."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        address = Address.objects.get(id=addressId)
        cart_details = CartDetails.objects.filter(cartId=cartId)
        rider = CustomUser.objects.get(id=riderId, user_type='rider')
    except (Address.DoesNotExist, CartDetails.DoesNotExist, CustomUser.DoesNotExist):
        return Response({"error": "Invalid cartId, addressId, or riderId."}, status=status.HTTP_404_NOT_FOUND)

    data = {
        "address": address,
        "cart_details": cart_details,
        "rider": rider,
    }

    serializer = FilteredDataSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)


   
@api_view(["POST"])  
def recieve_order_details(request):
    try:
        payload = request.data

        if "payload" not in payload:
            return Response({"error": "Invalid data: 'payload' key missing"}, status=status.HTTP_400_BAD_REQUEST)

        address = payload["payload"].get("address", "N/A")
        username = payload["payload"].get("username", "N/A")
        payment_mode = payload["payload"].get("payment_mode", "N/A")
        if payment_mode == "Easypaisa":
            payment_mode = 'online'
        transaction_id = payload["payload"].get("transaction_id", "N/A")
        total_price = payload["payload"].get("total_price", "N/A")
        items = payload["payload"].get("items", [])

        try:
            user = CustomUser.objects.get(username=username)
        except:
            return Response('can not find user', status=status.HTTP_404_NOT_FOUND)
        else:
            userID = user.id
            
        processed_items = []
        for item in items:
            processed_items.append({
                "item_id": item.get("id"),
                "quantity": item.get("quantity"),
                "price": item.get("price"),
            })

        for item in processed_items:
            try:
                itemDetail = invModels.Item.objects.get(id=item['item_id'])
            except:
                return Response('can not find item', status=status.HTTP_404_NOT_FOUND)
            else:
                itemDetail.current_qty -=  item['quantity']
                itemDetail.qty_sold +=  item['quantity']
                if 0 < itemDetail.current_qty < itemDetail.min_threshold_qty:
                    itemDetail.qty_status = 'insufficient'
                elif itemDetail.min_threshold_qty <= itemDetail.current_qty <= itemDetail.max_threshold_qty:
                    itemDetail.qty_status = 'sufficient'
                elif itemDetail.current_qty > itemDetail.max_threshold_qty:
                    itemDetail.qty_status = 'surplus'
                itemDetail.save()

        try:
            cart = Cart.objects.create(userID=user)
        except:
            return Response('can not initialize cart', status=status.HTTP_400_BAD_REQUEST)
        else:
            for item in processed_items:
                product = Item.objects.get(id=item['item_id'])
                CartDetails.objects.create(cartId=cart, prodId=product, prodPrice=item['price'], qty=item['quantity'])
            address = Address.objects.create(userID=user, address=address)
            if transaction_id:
                Order.objects.create(cartId=cart, address=address, net_total=total_price, payment_mode=payment_mode, transaction_id=transaction_id, payment_status='unpaid', order_status='pending')
            else:
                Order.objects.create(cartId=cart, address=address, net_total=total_price, payment_mode=payment_mode, payment_status='unpaid', order_status='pending')

            return Response('Order placed successfully.', status=status.HTTP_200_OK)      
    
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def medisuggestItems(request):

    queriedItem = request.data.get('search')

    if not queriedItem:
        return Response(
            {'detail': 'Search term is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    searchResult_item = invModels.Item.objects.filter(name=queriedItem)

    searchResult_formula = invModels.MedFormula.objects.filter(formula_name__icontains=queriedItem)

    searchResult_symptom = invModels.Symptom.objects.filter(symptom=queriedItem)

    items_from_formula = invModels.Item.objects.none()  
    items_from_symptom = invModels.Item.objects.none()  

    if searchResult_formula.exists():
        formula = searchResult_formula.first()
        items_from_formula = invModels.Item.objects.filter(med_formula=formula)

    if searchResult_symptom.exists():
        symptom = searchResult_symptom.first()
        related_formula = symptom.med_formula  
        if related_formula:
            items_from_symptom = invModels.Item.objects.filter(med_formula=related_formula)

    combined_items = searchResult_item.union(items_from_formula, items_from_symptom)

    serialized_items = OnlineItemSerializer(combined_items, many=True).data

    if serialized_items:
        return Response(
            {
                'searchResult': serialized_items,
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'detail': 'No matching items, formulas, or symptoms found.'},
            status=status.HTTP_404_NOT_FOUND
        )   
    

@api_view(['GET'])
def get_unique_symptoms(request):
    # Fetch unique symptom names
    unique_symptoms = Symptom.objects.values_list('symptom', flat=True).distinct()
    # unique_symptoms = UniqueSymptomSerializer(unique_symptoms, many=True).data
    # Format the response
    return Response({"unique_symptoms": unique_symptoms})
