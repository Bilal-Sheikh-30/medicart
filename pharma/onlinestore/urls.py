from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.loginFunction, name='loginpage'),
    path('signup/', views.signupFunction, name='signuppage'),
    path('logout/', LogoutView.as_view(next_page='homepage'), name='logout'),
    
]