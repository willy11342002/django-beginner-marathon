from django.urls import include
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', views.index, name='user_info'),
    path('', include('django.contrib.auth.urls')),
]
