from django.shortcuts import render
from .models import *
from onlinestore import models
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from onlinestore.models import *
from onlinestore.serializers import *
from django.core.mail import send_mail
from django.db.models import Q

from django.views.decorators.csrf import csrf_exempt


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
        'qty_status': 'finished',
    }

    item_serializer = ItemSerializer(data=item_data)

    # Check if an item with the same name and dosage strength already exists
    if Item.objects.filter(name=item_data['name'], dosage_strength=f"{item_data['dosage_strength']} {item_data['dosage_unit']}").exists():
        response_data['message'] = 'Item with the same name and dosage strength already exists'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    elif item_serializer.is_valid():
        item = item_serializer.save()

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

@api_view(['GET'])
def get_item(request, item_id):
    data = {
        'item' : '',
        'image' : ''
    }
    item = get_object_or_404(Item, id=item_id)
    if item:
        item = ItemSerializer(item)
        data['item'] = item.data
        try:
            image = get_object_or_404(MedImage, item_id=item_id)
            image = MedImageSerializer(image)
            data['image'] = image.data
        except:
            data['image'] = 'no image available.'
    return Response(data)

# low stock items will be displayed on the home of inventory
@api_view(['GET'])
def getLowStockItems(request):
    lowStocktems = Item.objects.filter(Q(qty_status='insufficient') | Q(qty_status='finished')).exclude(is_ordered=True)
    lowStocktems = ItemSerializer(lowStocktems, many=True).data
    return Response(lowStocktems)

@api_view(['POST'])
def orderByInv(request):
    data = request.data
    orderDetails = {
        'itemId' : data.get('itemId'),
        'qty' : data.get('qty'),
        'vendorId' : data.get('vendorId'),
    }

    vendor = get_object_or_404(Vendor, id=orderDetails['vendorId'])
    item = get_object_or_404(Item, id=orderDetails['itemId'])

    # Email configuration
    subject = f"Order for {item.name} {item.dosage_strength}"
    message = (
        f"Hello {vendor.name},\n\n"
        f"We would like to place an order for the following item:\n\n"
        f"Medicine Name: {item.name}\n"
        f"Dosage Strength: {item.dosage_strength}\n"
        f"Quantity: {orderDetails['qty']}\n\n"
        f"Please confirm the availability and expected delivery time.\n\n"
        f"Thank you,\n"
        f"Team MediCart"
    )
    recipient_email = vendor.email

    # Send the email
    try:
        send_mail(
            subject,
            message,
            'aadi64499@gmail.com',   # Replace with your email
            [recipient_email],
            fail_silently=False,
        )

    except:
        return Response({"message": "Failed to place order to the vendor."})
    else:
        item.is_ordered=True
        item.save()
        try:
            InventoryOrders.objects.create(
                itemId = item,
                qty_ordered = orderDetails['qty'],
                order_status = 'pending',
                vendorID = vendor
            )
        except:
            return Response({"message": "Email sent to Vendor but failed to update database!"})
        else:
            return Response({"message": "Order placed and email sent to the vendor."})

@api_view(['GET'])
def trackInvOrder(request):
    pending_orders = InventoryOrders.objects.filter(order_status='pending').order_by('-orderDate')
    pending_orders = InvOrderSerializer(pending_orders, many=True).data
    return Response(pending_orders)

@api_view(['POST'])
def receiveInvOrder(request):
    response_data = {'message': ''}
    orderInfo = request.data

    try:
        orderId = int(orderInfo.get('orderId'))
        receivedQty = int(orderInfo.get('receivedQty'))
    except (ValueError, TypeError):
        response_data['message'] = 'Invalid orderId or receivedQty provided.'
        return Response(response_data, status=400)

    try:
        order = InventoryOrders.objects.get(id=orderId)
        item = order.itemId  
    except InventoryOrders.DoesNotExist:
        response_data['message'] = 'Cannot find entry for this order in the database.'
        return Response(response_data, status=404)
    except Item.DoesNotExist:
        response_data['message'] = 'Cannot find associated item for this order in the database.'
        return Response(response_data, status=404)

    order.order_status = 'completed'
    order.qty_received = receivedQty
    print(f'prder: {order}')
    order.save()

    item.current_qty += receivedQty
    item.is_ordered = "False" 
    if 0 < item.current_qty < item.min_threshold_qty:
        item.qty_status = 'insufficient'
    elif item.min_threshold_qty <= item.current_qty <= item.max_threshold_qty:
        item.qty_status = 'sufficient'
    elif item.current_qty > item.max_threshold_qty:
        item.qty_status = 'surplus'
    print(f'item: {item}')
    item.save()

    response_data['message'] = 'Inventory updated successfully.'
    return Response(response_data)

# sales related views will go below
def sales(request):
    return render(request,'inv_layout.html')

@api_view(['GET'])
def pending_orders(request):
    pending_orders = Order.objects.filter(order_status="Pending")
    serialized_orders = OrderSerializer(pending_orders, many=True).data
    return Response(serialized_orders)


@api_view(['GET'])
def get_order_detail(request, order_id):
    data = {
        'order': '',
        'cart': []
    }

    try:
        # Fetch the order
        order = get_object_or_404(Order, id=order_id)
    except:
        return Response({'error': 'Cannot find order'}, status=404)

    try:
        # Fetch all cart details for the order
        cart_details = CartDetails.objects.filter(cartId=order.cartId_id)
    except:
        return Response({'error': 'Cannot find cart details'}, status=404)

    # Serialize the order
    order_serialized = OrderSerializer(order).data

    # Serialize each cart entry and add item details
    cart_serialized = []
    for cart_entry in cart_details:
        cart_data = CartSerializer(cart_entry).data

        # Fetch the item details for the product
        try:
            item = get_object_or_404(Item, id=cart_entry.prodId_id)
            item_data = ItemSerializer(item).data
            cart_data['item_details'] = item_data  # Append item details to the cart entry
        except:
            cart_data['item_details'] = {'error': 'Item not found'}

        cart_serialized.append(cart_data)

    # Combine the order and cart details
    data['order'] = order_serialized
    data['cart'] = cart_serialized

    return Response(data)

@api_view(['PUT'])
def edit_order(request, order_id):
    response_data = {'message': ''}

    try:
        # Fetch the item to be updated
        order = Order.objects.get(id=order_id)
    except Item.DoesNotExist:
        return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    # Extract updated item data from the request
    updated_data = {
        'net_total': request.data.get('net_total', order.net_total),
        'payment_mode': request.data.get('payment_mode', order.payment_mode),
        'payment_receipt': request.data.get('med_formula', order.payment_receipt),
        'payment_status': request.data.get('payment_status', order.payment_status),
        'address_id': request.data.get('address_id', order.address_id),
        'cartId_id': request.data.get('cartId_id', order.cartId_id),
        'rider_id': request.data.get('rider_id',order.rider_id),  
        'order_status': request.data.get('order_status', order.order_status),
    }

    # Serialize and validate the updated data
    order_serializer = OrderSerializer(order, data=updated_data, partial=True)

    # Validate and update item
    if order_serializer.is_valid():
        order_serializer.save()
        # Check if order_status is updated to 'shipped'
        if updated_data.get('order_status') == 'shipped':
        # Email configuration
            subject = f"Order Update: Your Order #{order.id} Has Been Shipped"
            message = (
                f"Dear {order.cartId.userID.first_name} {order.cartId.userID.last_name},\n\n"
                f"Your order with ID {order.id} has been shipped.\n"
                f"Here are the order details:\n"
                f"Net Total: {order.net_total}\n"
                f"Payment Mode: {order.payment_mode}\n\n"
                f"Thank you for choosing us.\n"
                f"Team MediCart"
            )
            recipient_email = order.user.email  # Assuming order.user.email exists

            # Send the email
            try:
                send_mail(
                    subject,
                    message,
                    'aadi64499@gmail.com',  # Replace with your email
                    [recipient_email],
                    fail_silently=False,
                )
                response_data['email_message'] = 'Email notification sent to the user.'
            except Exception as e:
                response_data['email_message'] = f"Failed to send email: {str(e)}"
        # email end
        response_data['message'] = 'Order updated successfully.'
        return Response(response_data, status=status.HTTP_200_OK)

    return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views related to rider will go below
def rider(request):
    return render(request,'inv_layout.html')