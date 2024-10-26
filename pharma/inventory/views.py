from django.shortcuts import render
from .models import Company, MedCategory, MedFormula
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

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

def viewcategory(request):
    categories = MedCategory.objects.all()
    return render(request,'viewcategory.html', {'categories': categories})

def addcategory(request):
    if request.method == 'POST':
       category_name = request.POST.get('category_name')
       if MedCategory.objects.filter(category_name=category_name).exists():
           messages.error(request,'Category already exists!')
       else:
           MedCategory.objects.create(category_name=category_name)
           messages.success(request,'Category added.')
    return render(request, 'addcategory.html')

def editcategory(request, category_id):
    category = get_object_or_404(MedCategory, id=category_id)
    if request.method == 'POST':
        new_category_name = request.POST.get('category_name')
        if MedCategory.objects.filter(category_name=new_category_name).exclude(id=category_id).exists():
            messages.error(request, 'Category name already exists!')
        else:
            category.category_name = new_category_name
            category.save()
            messages.success(request, 'Category updated successfully.')

    return render(request, 'addcategory.html', {'category': category})

def viewformulae(request):
    formulae = MedFormula.objects.all()
    return render(request,'viewformula.html', {'formulae': formulae})

def addformula(request):
    if request.method == 'POST':
       formula_name = request.POST.get('formula_name')
       if MedFormula.objects.filter(formula_name=formula_name).exists():
           messages.error(request,'Formula already exists!')
       else:
           MedFormula.objects.create(formula_name=formula_name)
           messages.success(request,'Formula added.')
    return render(request, 'addformula.html')

def editformula(request, formula_id):
    formula = get_object_or_404(MedFormula, id=formula_id)
    if request.method == 'POST':
        new_formula_name = request.POST.get('formula_name')
        if MedFormula.objects.filter(formula_name=new_formula_name).exclude(id=formula_id).exists():
            messages.error(request, 'Formula name already exists!')
        else:
            formula.formula_name = new_formula_name
            formula.save()
            messages.success(request, 'Formula Name updated successfully.')

    return render(request, 'addformula.html', {'formula': formula})

def sales(request):
    return render(request,'inv_layout.html')

def rider(request):
    return render(request,'inv_layout.html')