from django.urls import path
from django.conf.urls import url
from . import views
from rest_framework import routers
from bitmex.views import ParameterViewSet, ThresholdViewSet, LevelsAPIView, FundingAPIView

router = routers.DefaultRouter(trailing_slash=True)

router.register("parameters", ParameterViewSet)
router.register("thresholds", ThresholdViewSet)

urlpatterns = [
    path('', views.bitmex_dashboard, name='bitmex_dashboard'),
    # path('update_support_resistance', views.update_support_resistance, name='update_support_resistance'),
    # path('update_funding_rates', views.update_funding_rates, name='update_funding_rates'),
    # path('update_volume_1m', views.update_volume_1m, name='update_volume_1m'),
    # path('update_volume_5m', views.update_volume_5m, name='update_volume_5m'),
    # path('update_trade_volume', views.update_trade_volume, name='update_trade_volume'),
    # path('update_current_price', views.update_current_price, name='update_current_price'),
    # path('test', views.test, name='test'),
    path('feeder', views.feeder, name='feeder')
]

urlpatterns.extend(router.urls)
urlpatterns.extend([
    url("parameters", ParameterViewSet),
    url("funding", FundingAPIView.as_view()),
    url("levels", LevelsAPIView.as_view()),
])