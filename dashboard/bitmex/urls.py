from django.urls import path
from . import views

urlpatterns = [
    path('', views.bitmex_dashboard, name='bitmex_dashboard'),
    path('update_funding_rates', views.update_funding_rates, name='update_funding_rates'),
    path('update_volume_1m', views.update_volume_1m, name='update_volume_1m'),
    path('update_volume_5m', views.update_volume_5m, name='update_volume_5m'),
    path('update_trade_volume', views.update_trade_volume, name='update_trade_volume'),
    path('update_current_price', views.update_current_price, name='update_current_price'),
    path('test', views.test, name='test'),
    path('feeder', views.feeder, name='feeder')
]