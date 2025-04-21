from django.urls import path
from . import views


urlpatterns = [
    path('', views.get_ads, name='get_ads'),
    path('my_ads/', views.get_my_ads, name='get_my_ads'),
    path('user/<int:id>/', views.get_user_ads, name='get_user_ads'),
    path('exchange/', views.get_exchange, name='get_exchange'),
    path('create/', views.create_ad, name='create_ad'),
    path('edit/<int:id>', views.edit_ad, name='edit_ad'),
    path('delete/<int:id>', views.delete_ad, name='delete_ad'),
    path('exchange/create/<int:id>', views.create_exchange, name='create_exchange'),
]