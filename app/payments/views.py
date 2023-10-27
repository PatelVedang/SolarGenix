import stripe
from rest_framework import status
from rest_framework import generics, viewsets
from .models import PaymentHistory
from datetime import datetime, timezone

from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY
publishable_key= settings.STRIPE_PUBLISHABLE_KEY

from utils.make_response import response
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework.decorators import action
from user.models import User

@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Pricings'], operation_description= "List API.", operation_summary="API to get list of records."))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Pricings'], operation_description= "Retrieve API.", operation_summary="API for retrieve single record by id."))
class PricingView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        prices = stripe.Price.list(
            expand=['data.product'],
            active=True
            # order={"by": [{"created": "desc"}]}
        )
        prices['data'] = prices['data'][::-1]
        prices['publishable_key']=publishable_key
        today = datetime.utcnow()
        active_subscriptions = PaymentHistory.objects.filter(status=1, current_period_start__lte=today, current_period_end__gte=today, user=request.user.id)
        serializer = PaymentHistorySerializer(active_subscriptions, many=True)
        prices['active_subscription'] = serializer.data
        return response(data=prices, status_code=status.HTTP_200_OK, message="Pricing found.")
    
    def retrieve(self, request, *args, **kwargs):
        prices = stripe.Price.retrieve(
            id=kwargs.get('pk')
        )
        prices['publishable_key']=publishable_key
        return response(data=prices, status_code=status.HTTP_200_OK, message="Pricing found.")
    
class ConfigView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        data = {
            'publishable_key': publishable_key
        }
        return response(data=data, status_code=status.HTTP_200_OK, message="Config found.")


class PaymentCallbackView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            payment_intent=kwargs.get('pk')
            if not payment_intent:
                return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="something went wrong")
            intent = stripe.PaymentIntent.retrieve(
                payment_intent,
                expand=['payment_method'])
            
            subscription = stripe.Subscription.create(
                customer=intent['metadata']['customer'],
                items=[{
                    'price': intent['metadata']['price'],
                }],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
            )
            product_id = subscription['items']['data'][0]['price']['product']
            product = stripe.Product.retrieve(product_id)
            metadata = product.get('metadata', {})
            if not metadata:
                return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="something went wrong")
            
            PaymentHistory.objects.create(
                user=User(id=request.user.id),
                stripe_subscription_id=subscription['id'],
                price_id=intent['metadata']['price'],
                status = 1,
                current_period_start = datetime.utcfromtimestamp(subscription['current_period_start']).replace(tzinfo=timezone.utc),
                current_period_end = datetime.utcfromtimestamp(subscription['current_period_end']).replace(tzinfo=timezone.utc),
                ip_limit = int(metadata.get('ip_limit','1'))
            )
        
        except stripe.error.StripeError as e:
            print(e,"Stripe Error")
            return response(data={}, status_code=status.HTTP_400_BAD_REQUEST, message=str(e))
        except Exception as e:
            return response(data={}, status_code=status.HTTP_400_BAD_REQUEST, message=str(e))
        
        return response(data={}, status_code=status.HTTP_200_OK, message="Success")



@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Checkout'], operation_description= "Retrieve API.", operation_summary="API for retrieve single record by id."))
class CheckoutView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            price = stripe.Price.retrieve(
                id=kwargs.get('pk')
            )
            if not price:
                return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="something went wrong")

            intent = stripe.PaymentIntent.create(
                description="Software development services",
                amount=price['unit_amount_decimal'],
                currency="cad",
                payment_method_types=["card"],
                metadata={
                    'customer': request.user.stripe_customer_id,
                    'price': price['id']
                }
            )
            data = {
                'publishable_key': publishable_key,
                'client_secret': intent.client_secret
            }
            return response(data=data, status_code=status.HTTP_200_OK, message="Intent created.")

        except stripe.error.StripeError as e:
            return response(data={}, status_code=status.HTTP_400_BAD_REQUEST, message=str(e))
        except Exception as e:
            return response(data={}, status_code=status.HTTP_400_BAD_REQUEST, message=str(e))
    

@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Plan'], operation_description= "List API.", operation_summary="API to get list of records."))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Plan'], operation_description= "Retrieve API.", operation_summary="API for retrieve single record by id."))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Plan'], auto_schema=None))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Plan'], auto_schema=None))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Plan'], auto_schema=None))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Plan'], auto_schema=None))
class PaymentHistoryView(viewsets.ModelViewSet):
    queryset = PaymentHistory.objects.all()
    serializer_class = PaymentHistorySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method = 'get',
        operation_description= "Get user subscription",
        operation_summary="API to get user subscriptions.",
        request_body=None,
        tags=['Plan']

    )
    @action(methods=['GET'], detail=False, url_path="active")
    def get_active_user_plan(self, request, *args, **kwargs):
        today = datetime.utcnow()
        if request.user.role == 1:
            active_subscriptions = PaymentHistory.objects.filter(status=1, current_period_start__lte=today, current_period_end__gte=today)
        else:
            active_subscriptions = PaymentHistory.objects.filter(status=1, current_period_start__lte=today, current_period_end__gte=today, user=request.user.id)

        serializer = self.get_serializer(active_subscriptions, many=True)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def list(self, request, *args, **kwargs):
        serializer = super().list(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")
    
    def retrieve(self, request, *args, **kwargs):
        serializer = super().retrieve(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

class CreateSubscriptionView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionPayloadSerializer
        
    @swagger_auto_schema(
        tags=['Payment'],
        operation_description= "API to create stripe subscription",
        operation_summary="API to create stripe subscription"
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                # Create the subscription
                subscription = stripe.Subscription.create(
                    customer=request.user.stripe_customer_id,
                    items=[{
                        'price': serializer.validated_data['price_id'],
                    }],
                    payment_behavior='default_incomplete',
                    expand=['latest_invoice.payment_intent'],
                )
                print(subscription, "=>>>Subscription CReated")
                return response(data={}, status_code=status.HTTP_200_OK, message="subscription created successfully.")
            except Exception as e:
                return response(data={}, status_code=status.HTTP_400_BAD_REQUEST, message=str(e))

