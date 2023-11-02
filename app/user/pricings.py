import stripe
from django.conf import settings
stripe.api_key=settings.STRIPE_SECRET_KEY
import json

items=[
    [
        'FREE',
        'plan A',
        {
            'feature_1' : 'Access to Scanning Portal__check_mark',
            'feature_2' : 'Access to limited executive report__check_mark',
            'feature_3' : 'Full scan for 1 IP every 15 days__check_mark',
            'feature_4' : 'Vulnerability scan for 1 domain or IP address__check_mark',
            'feature_5' : 'Data leak scan for unlimited number of email addresses__cross_mark',
            'feature_6' : 'Automatic discovery of domain-associated email addresses__cross_mark',
            'feature_7' : 'Quarterly trend reporting__cross_mark',
            'feature_8' : 'High level Maturity audit and cybersecurity road map (cybersecurity posture, Bill 25, etc)__cross_mark',
            'feature_9' : 'Dedicated world class cybersecurity team with 3 decades of experience__cross_mark',
            'feature_10' : '24×7 toll free crisis hotline__cross_mark',
            'feature_11' : 'Yearly senior management cybersecurity training__cross_mark',
            'feature_12' : 'Service support portal__cross_mark',
            'feature_13' : '+30% off hourly rate for cybersecurity services__cross_mark',
            'credit': 100,
            'ip_limit': 1,
            'bg_color':'#f8f4f4',
            'color':'black',
            'short_desc':'No hidden fees!',
            'detail_desc':'Perform a free scan to get an idea where your vulnerabilities lie',
            'button_disable':1,
            'button_text':'Selected',
            'interval': 'fixed'
        },
        0,
        'cad',
        {}
    ],
    [
        'SINGLE USE',
        'plan B',
        {
            'feature_1' : 'Access to Scanning Portal__check_mark',
            'feature_2' : 'Access to limited executive report & CSV report of scan results__check_mark',
            'feature_3' : '1 scan per domain__check_mark',
            'feature_4' : 'Vulnerability scan for 2 domain or IP address__check_mark',
            'feature_5' : 'Data leak scan for unlimited number of email addresses__cross_mark',
            'feature_6' : 'Automatic discovery of domain-associated email addresses__cross_mark',
            'feature_7' : 'Quarterly trend reporting__cross_mark',
            'feature_8' : 'High level Maturity audit and cybersecurity road map (cybersecurity posture, Bill 25, etc)__cross_mark',
            'feature_9' : 'Dedicated world class cybersecurity team with 3 decades of experience__cross_mark',
            'feature_10' : '24×7 toll free crisis hotline__cross_mark',
            'feature_11' : 'Yearly senior management cybersecurity training__cross_mark',
            'feature_12' : 'Service support portal__cross_mark',
            'feature_13' : '+30% off hourly rate for cybersecurity services__cross_mark',
            'credit': 100,
            'ip_limit': 2,
            'bg_color':'#f8f4f4',
            'color':'black',
            'short_desc':'+$249 for the executive report',
            'detail_desc':'Get a quick view of what services and potentially exploitable external vulnerabilities you have that criminals can leverage',
            'button_disable':0,
            'button_text':'Get started',
            'interval': 'fixed'
        },
        29900,
        'cad',
        {}
    ],
    [
        'LEVEL ONE',
        'plan C',
        {
            'feature_1' : 'Access to Scanning Portal__check_mark',
            'feature_2' : 'Entire executive report with actionable steps__check_mark',
            'feature_3' : '1 scan per month per domain__check_mark',
            'feature_4' : 'Vulnerability scan for 5 domains or IP addresses__check_mark',
            'feature_5' : 'Data leak scan for unlimited number of email addresses__check_mark',
            'feature_6' : 'Automatic discovery of domain-associated email addresses__check_mark',
            'feature_7' : 'Quarterly trend reporting__check_mark',
            'feature_8' : 'High level Maturity audit and cybersecurity road map (cybersecurity posture, Bill 25, etc)__cross_mark',
            'feature_9' : 'Dedicated world class cybersecurity team with 3 decades of experience__cross_mark',
            'feature_10' : '24×7 toll free crisis hotline__cross_mark',
            'feature_11' : 'Yearly senior management cybersecurity training__cross_mark',
            'feature_12' : 'Service support portal__cross_mark',
            'feature_13' : '+30% off hourly rate for cybersecurity services__cross_mark',
            'credit': 100,
            'ip_limit': 5,
            'bg_color':'#ff7c5c',
            'color':'white',
            'short_desc':'Billed monthly',
            'detail_desc':'For organizations that want to keep an active eye on their external vulnerabilities with monthly tests including data leak identification',
            'button_disable':0,
            'button_text':'Get started',
            'interval': 'month'
        },
        19900,
        'cad',
        {
            'interval': 'month'
        }
    ],
    [
        'LEVEL TWO',
        'plan D',
        {
            'feature_1' : 'Access to Scanning Portal__check_mark',
            'feature_2' : 'Entire executive report with actionable steps__check_mark',
            'feature_3' : '1 scan per month per domain__check_mark',
            'feature_4' : 'Vulnerability scan for 5 domains or IP addresses__check_mark',
            'feature_5' : 'Data leak scan for unlimited number of email addresses__check_mark',
            'feature_6' : 'Automatic discovery of domain-associated email addresses__check_mark',
            'feature_7' : 'Quarterly trend reporting__check_mark',
            'feature_8' : 'High level Maturity audit and cybersecurity road map (cybersecurity posture, Bill 25, etc)__check_mark',
            'feature_9' : 'Dedicated world class cybersecurity team with 3 decades of experience__check_mark',
            'feature_10' : '24×7 toll free crisis hotline__check_mark',
            'feature_11' : 'Yearly senior management cybersecurity training__check_mark',
            'feature_12' : 'Service support portal__check_mark',
            'feature_13' : '+30% off hourly rate for cybersecurity services__check_mark',
            'credit': 100,
            'ip_limit': 5,
            'bg_color':'#f8f4f4',
            'color':'black',
            'short_desc':'Billed monthly',
            'detail_desc':'For organizations that are dependant on technology and want to know what their next steps are for optimizing their cybersecurity posture',
            'button_disable':0,
            'button_text':'Get started',
            'interval': 'month'
        },
        69900,
        'cad',
        {
            'interval': 'month'
        }
    ],
    [
        'LEVEL ONE',
        'plan E',
        {
            'feature_1' : 'Access to Scanning Portal__check_mark',
            'feature_2' : 'Entire executive report with actionable steps__check_mark',
            'feature_3' : '1 scan per month per domain__check_mark',
            'feature_4' : 'Vulnerability scan for 5 domains or IP addresses__check_mark',
            'feature_5' : 'Data leak scan for unlimited number of email addresses__check_mark',
            'feature_6' : 'Automatic discovery of domain-associated email addresses__check_mark',
            'feature_7' : 'Quarterly trend reporting__check_mark',
            'feature_8' : 'High level Maturity audit and cybersecurity road map (cybersecurity posture, Bill 25, etc)__cross_mark',
            'feature_9' : 'Dedicated world class cybersecurity team with 3 decades of experience__cross_mark',
            'feature_10' : '24×7 toll free crisis hotline__cross_mark',
            'feature_11' : 'Yearly senior management cybersecurity training__cross_mark',
            'feature_12' : 'Service support portal__cross_mark',
            'feature_13' : '+30% off hourly rate for cybersecurity services__cross_mark',
            'credit': 100,
            'ip_limit': 5,
            'bg_color':'#ff7c5c',
            'color':'white',
            'short_desc':'Billed annually',
            'detail_desc':'For organizations that want to keep an active eye on their external vulnerabilities with monthly tests including data leak identification',
            'button_disable':0,
            'button_text':'Get started',
            'interval': 'year'
        },
        240000,
        'cad',
        {
            'interval': 'year'
        }
    ],
    [
        'LEVEL TWO',
        'plan F',
        {
            'feature_1' : 'Access to Scanning Portal__check_mark',
            'feature_2' : 'Entire executive report with actionable steps__check_mark',
            'feature_3' : '1 scan per month per domain__check_mark',
            'feature_4' : 'Vulnerability scan for 5 domains or IP addresses__check_mark',
            'feature_5' : 'Data leak scan for unlimited number of email addresses__check_mark',
            'feature_6' : 'Automatic discovery of domain-associated email addresses__check_mark',
            'feature_7' : 'Quarterly trend reporting__check_mark',
            'feature_8' : 'High level Maturity audit and cybersecurity road map (cybersecurity posture, Bill 25, etc)__check_mark',
            'feature_9' : 'Dedicated world class cybersecurity team with 3 decades of experience__check_mark',
            'feature_10' : '24×7 toll free crisis hotline__check_mark',
            'feature_11' : 'Yearly senior management cybersecurity training__check_mark',
            'feature_12' : 'Service support portal__check_mark',
            'feature_13' : '+30% off hourly rate for cybersecurity services__check_mark',
            'credit': 100,
            'ip_limit': 5,
            'bg_color':'#f8f4f4',
            'color':'black',
            'short_desc':'Billed annually',
            'detail_desc':'For organizations that are dependant on technology and want to know what their next steps are for optimizing their cybersecurity posture',
            'button_disable':0,
            'button_text':'Get started',
            'interval': 'year'
        },
        800000,
        'cad',
        {
            'interval': 'year'
        }
    ]
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
