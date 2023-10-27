import stripe
from django.conf import settings
stripe.api_key=settings.STRIPE_SECRET_KEY
items=[
    [
        'Basic',
        'Monthly basic plan',
        {
            'feature': 'Vulnerability scan for 2 domains or IP addresses',
            'credit': 100,
            'ip_limit': 2
        },
        1000,
        'cad',
        {
            'interval': 'month'
        }
    ],
    [
        'Basic',
        'Yearly basic plan',
        {
            'feature': 'Vulnerability scan for 20 domains or IP addresses',
            'credit': 1000,
            'ip_limit': 20
        },
        10000,
        'cad',
        {
            'interval': 'year'
        }
    ],
    [
        'Advance',
        'Monthly advance plan',
        {
            'feature': 'Vulnerability scan for 5 domains or IP addresses',
            'credit': 200,
            'ip_limit': 5
        },
        2000,
        'cad',
        {
            'interval': 'month'
        }
    ],
    [
        'Advance',
        'Yearly advance plan',
        {
            'feature': 'Vulnerability scan for 50 domains or IP addresses',
            'credit': 2000,
            'ip_limit': 50
        },
        20000,
        'cad',
        {
            'interval': 'year'
        }
    ],
    [
        'Enterprise',
        'Monthly enterprise plan',
        {
            'feature': 'Vulnerability scan for 10 domains or IP addresses',
            'credit': 500,
            'ip_limit': 10
        },
        5000,
        'cad',
        {
            'interval': 'month'
        }
    ],
    [
        'Enterprise',
        'Yearly enterprise plan',
        {
            'feature': 'Vulnerability scan for 100 domains or IP addresses',
            'credit': 5000,
            'ip_limit': 100
        },
        50000,
        'cad',
        {
            'interval': 'year'
        }
    ],
    
]
for item in items:
    # Create a product
    product = stripe.Product.create(
        name=item[0],
        description=item[1],
        metadata=item[2]
    )

    # Create a price for the product (recurring)
    price = stripe.Price.create(
        product=product.id,
        unit_amount=item[3],
        currency=item[4],
        recurring=item[5]
    )
