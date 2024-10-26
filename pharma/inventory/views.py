from django.shortcuts import render
from .models import Company
from django.contrib import messages
# Create your views here.

def warehouse(request):
    return render(request,'warehouse_landing.html')

def allcompanies(request):
    companies = Company.objects.all()
    return render(request,'allcompanies.html', {'companies':companies})

def addcompany(request):
    if request.method == 'POST':
       company_name = request.POST.get('company_name')
       if Company.objects.filter(name=company_name).exists():
           messages.error(request,'Company already exists!')
       else:
           Company.objects.create(name=company_name)
           messages.success(request,'added successfully!!')
    return render(request,'addcompany.html')

def sales(request):
    return render(request,'inv_layout.html')

def rider(request):
    return render(request,'inv_layout.html')