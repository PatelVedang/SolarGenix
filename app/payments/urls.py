from django.urls import path, include
from payments import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('config', views.ConfigView,basename='config')
router.register('pricings', views.PricingView, basename='pricings')
router.register('checkout', views.CheckoutView, basename='checkout')
router.register('payment/next', views.PaymentCallbackView, basename='payment')
router.register('plan', views.PaymentHistoryView, basename='plan')

urlpatterns = [
    path('', include(router.urls)),
    path('payment/create-subscription', views.CreateSubscriptionView.as_view(), name='create-subscription'),
    path('payment/webhook', views.StripeWebHooks.as_view(), name='webhook')
]