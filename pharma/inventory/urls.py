from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from onlinestore.views import homepage

app_name = 'inventory'

urlpatterns = [
    # path('', views.homepage, name='homepage'),
    path('warehouse/', views.warehouse, name='warehousepage'),
    path('sales/', views.sales, name='salespage'),
    path('rider/', views.rider, name='riderpage'),
    path('allcompanies/', views.allcompanies, name='allcompaniespage'),
    path('addcompany/', views.addcompany, name='addcompanypage'),
    path('logout/', LogoutView.as_view(next_page=homepage), name='logout'),
]