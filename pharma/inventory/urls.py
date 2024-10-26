from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from onlinestore.views import homepage

app_name = 'inventory'

urlpatterns = [
    path('warehouse/', views.warehouse, name='warehousepage'),
    path('sales/', views.sales, name='salespage'),
    path('rider/', views.rider, name='riderpage'),
    path('allcompanies/', views.allcompanies, name='allcompaniespage'),
    path('addcompany/', views.addcompany, name='addcompanypage'),
    path('viewcategory/', views.viewcategory, name='viewcategorypage'),
    path('addcategory/', views.addcategory, name='addcategorypage'),
    path('editcategory/<int:category_id>/', views.editcategory, name='editcategorypage'),
    path('viewformulae/', views.viewformulae, name='viewformulaepage'),
    path('addformula/', views.addformula, name='addformulapage'),
    path('editformula/<int:formula_id>/', views.editformula, name='editformulapage'),
    path('logout/', LogoutView.as_view(next_page=homepage), name='logout'),
]