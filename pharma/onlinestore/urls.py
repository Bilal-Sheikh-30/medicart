from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.loginFunction, name='loginpage'),
    path('signup/', views.signupFunction, name='signuppage'),
    path('itemByCategory/<int:catgId>/', views.itemByCategory, name='itemByCategory'),
    path('getHotItems/', views.getHotItems, name='getHotItems'),
    path('searchItems/', views.searchItems, name='searchItems'),
    path('medisuggestItems/', views.medisuggestItems, name='medisuggestItems'),
    
    path('getuniquesymptoms/', views.get_unique_symptoms, name='etuniquesymptoms'),
    path('logout/', LogoutView.as_view(next_page='homepage'), name='logout'),
    path('getqr/', views.getqr, name='getqr'),
    path('getOrderHistory/', views.getOrderHistory, name='getOrderHistory'),
    path('getOrderDetails/<int:cartId>/<int:addressId>/<int:riderId>/', views.getFilteredOrderDetails, name='getFilteredOrderDetails'),
    path('postorder/', views.recieve_order_details, name='getOrderHistory'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)