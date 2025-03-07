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
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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

@api_view(['GET'])
def allitems(request):
    items = Item.objects.all()
    # med_images = MedImage.objects.all()

    serialized_items = OnlineItemSerializer(items, many=True).data
    # serialized_images = MedImageSerializer(med_images,many=True).data

    data = {
        "items" : serialized_items,
        # "images" : serialized_images
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
    lowStocktems = OnlineItemSerializer(lowStocktems, many=True).data
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
    # Fetch pending orders and related item information
    pending_orders = InventoryOrders.objects.filter(order_status='pending').order_by('-orderDate')
    
    # Adding item information manually to the response
    response_data = []
    for order in pending_orders:
        # Fetch the first image for the current itemId
        image = MedImage.objects.filter(item_id=order.itemId.id) # Corrected to use .first()
        image= MedImageSerializer(image ,many=True).data
        # Only store the image URL if image exists
        image_url = image if image else None
        
        response_data.append({
            "id": order.id,
            "orderDate": order.orderDate,
            "qty_ordered": order.qty_ordered,
            "qty_received": order.qty_received,
            "order_status": order.order_status,
            "itemId": order.itemId.id,
            "vendorID": order.vendorID.id,
            "info": {
                "item_name": order.itemId.name,
                "item_description": order.itemId.description,
                "item_price": order.itemId.price,
                "vendor_name": order.vendorID.name,
                "image": image_url,  # Provide only the image URL
            }
        })
    
    return Response(response_data)



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
    def update_item_inventory(cart_item):
        try:
            item = cart_item.prodId
            item.qty_sold -= cart_item.qty
            item.current_qty += cart_item.qty

            # Update inventory status
            if 0 < item.current_qty < item.min_threshold_qty:
                item.qty_status = 'insufficient'
            elif item.min_threshold_qty <= item.current_qty <= item.max_threshold_qty:
                item.qty_status = 'sufficient'
            elif item.current_qty > item.max_threshold_qty:
                item.qty_status = 'surplus'

            item.save()
            return True
        except Exception as e:
            print(f'Error updating inventory for item {cart_item.prodId.id}: {e}')
            return False

    def send_order_email(order, user):
        subject = f"Order Update for: {order.id}"
        if order.order_status == 'cancelled':
            message = (
                f"Dear {user.first_name} {user.last_name},\n\n"
                f"Your order with ID {order.id} could not be shipped due to unverified payment.\n"
                f"Sorry for the inconvenience.\n\n"
                f"Team MediCart"
            )
        else:
            message = (
                f"Dear {user.first_name} {user.last_name},\n\n"
                f"Your order with ID {order.id} has been shipped.\n"
                f"Net Total: {order.net_total}\n"
                f"Payment Mode: {order.payment_mode}\n\n"
                f"Thank you for choosing us.\n\n"
                f"Team MediCart"
            )

        try:
            send_mail(subject, message, 'your_email@example.com', [user.email], fail_silently=False)
            print(f"Email sent to {user.email}")
            return True
        except Exception as e:
            print(f'Error sending email: {e}')
            return False

    payment_status = request.data.get('payment_status')
    rider_id = request.data.get('riderId')
    response_data = {'message': ''}

    try:
        order = Order.objects.get(id=order_id)
        user = order.cartId.userID
    except Order.DoesNotExist:
        return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    failed_updates = []
    try:
        with transaction.atomic():  
            if order.payment_mode == 'online' and payment_status == 'paid':
                if rider_id:
                    rider = get_object_or_404(CustomUser, id=rider_id, user_type='rider')
                    order.rider = rider
                order.payment_status = 'paid'
                order.order_status = 'shipped'
            elif order.payment_mode == 'online' and payment_status == 'unpaid':
                order.payment_status = 'unpaid'
                order.order_status = 'cancelled'

                # Update inventory
                cart_items = CartDetails.objects.filter(cartId=order.cartId)
                for cart_item in cart_items:
                    if not update_item_inventory(cart_item):
                        failed_updates.append(cart_item.prodId.id)
            else:
                if rider_id:
                    rider = get_object_or_404(CustomUser, id=rider_id, user_type='rider')
                    order.rider = rider
                order.order_status = 'shipped'

            order.save()
    except Exception as e:
        response_data['message'] = f"Error updating order: {e}"
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # Send order update email
    email_status = send_order_email(order, user)
    if email_status:
        if failed_updates:
            response_data['message'] = f"Order updated, email sent, but failed inventory updates for items: {failed_updates}."
        else:
            response_data['message'] = 'Order updated successfully, email sent.'
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data['message'] = 'Order updated, but email failed.'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

# views related to rider will go below

@api_view(['GET'])
def getvendors(request):

    vendors = Vendor.objects.all()
    vendors = VendorSerializer(vendors, many=True).data
    return Response(vendors, status=status.HTTP_200_OK)

@api_view(["GET"])
def getrider(request):
    riders = CustomUser.objects.filter(user_type='rider')
    riders = UserSerializer(riders, many=True).data
    return Response(riders, status=status.HTTP_200_OK)

@api_view(["GET"])
def showrides(request):
    assignedOrders = Order.objects.filter(order_status='shipped')
    print(assignedOrders)
    if assignedOrders.exists():
        assignedOrders = OrderSerializerforRider(assignedOrders, many=True).data
        return Response(assignedOrders, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "No assigned orders found."}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['PATCH'])
def deliveryupdate(request, orderID):
    deliveryStatus = request.data.get('deliveryStatus')
    try:
        order = Order.objects.get(id=orderID)
        # if request.user != order.rider:
        #     return Response('Unauthorized Access', status=status.HTTP_400_BAD_REQUEST)
    except Order.DoesNotExist:
        return Response('Can not find order.', status=status.HTTP_404_NOT_FOUND)
    
    if deliveryStatus == 'completed':
        order.payment_status = 'paid'
        order.order_status = 'completed'
    else:
        order.order_status = 'cancelled'
        
        try:
            cart = Cart.objects.get(id=order.cartId.id)
        except Cart.DoesNotExist:
            return Response('Cart not found', status=status.HTTP_404_NOT_FOUND)
        
        cartItems = CartDetails.objects.filter(cartId=cart)
        if not cartItems.exists():
            return Response('No items found in the cart', status=status.HTTP_404_NOT_FOUND)
        
        for item in cartItems:
            try:
                itemfromDb = Item.objects.get(id=item.prodId.id)
            except Item.DoesNotExist:
                continue  
            
            itemfromDb.qty_sold -= item.qty
            itemfromDb.current_qty += item.qty
            
            if 0 < itemfromDb.current_qty < itemfromDb.min_threshold_qty:
                itemfromDb.qty_status = 'insufficient'
            elif itemfromDb.min_threshold_qty <= itemfromDb.current_qty <= itemfromDb.max_threshold_qty:
                itemfromDb.qty_status = 'sufficient'
            elif itemfromDb.current_qty > itemfromDb.max_threshold_qty:
                itemfromDb.qty_status = 'surplus'
            
            print(itemfromDb.current_qty)
            itemfromDb.save()
        
    print(f'order: {order.order_status}')
    order.save()
    
    return Response('Order updated successfully', status=status.HTTP_200_OK)
