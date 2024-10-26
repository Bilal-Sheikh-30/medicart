from django.shortcuts import render, redirect
from inventory.models import CustomUser
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
# Create your views here.

def homepage(request):
    return render(request, 'homepage.html')

def loginFunction(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == 'user':
                # for general users
                return redirect('homepage')
            elif user.user_type == 'warehouse':
                return redirect(reverse('inventory:warehousepage'))
            elif user.user_type == 'sales':
                return redirect(reverse('inventory:salespage'))
            elif user.user_type == 'rider':
                return redirect(reverse('inventory:riderpage'))
            else:
                return redirect('homepage')
        else:
            messages.error(request,'Invalid Credentials.')
    return render(request,'registeration/login.html')

def signupFunction(request):
    if request.method == 'POST':
       first_name = request.POST.get('first_name')
       last_name = request.POST.get('last_name')
       email = request.POST.get('email')
       username = request.POST.get('username')
       password = request.POST.get('password')
       gender = request.POST.get('gender')
       if CustomUser.objects.filter(email = email).exists():
          messages.error(request,'email already exist. Can not register.')   
       elif CustomUser.objects.filter(username = username).exists():
           messages.error(request,'username already exist. Can not register.')
       else:
          newUser = CustomUser.objects.create_user(
              username = username,
              password = password,
              email = email,
              first_name = first_name,
              last_name = last_name,
              user_type = 'user',
              gender = gender
          )
          if newUser is not None:
              login(request, newUser)
              return redirect('homepage')
          else:
              messages.error(request, 'Failed to register.')
    return render(request,'registeration/signup.html')