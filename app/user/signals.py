from django.db.models.signals import pre_save
from django.dispatch import receiver
from user.models import User
import threading
from utils.email import send_email
from django.conf import settings

@receiver(pre_save, sender=User)
def user_verify_signal(sender, instance, **kwargs):
    # Only on update method 
    if not instance._state.adding:
        # Getting old record
        old_user = User.objects.get(email=instance.email)
        
        # Getting updated record
        new_user = instance

        old_is_verified = old_user.is_verified
        new_is_verified = new_user.is_verified
        if old_is_verified != new_is_verified:
            # If the status of is_verified is change to True from False
            if new_is_verified:

                # Sending the user account activation mail to end_user
                user_name = f"{new_user.first_name} {new_user.last_name}".upper()
                email_body =  f'''
                Dear {user_name},

                We're excited to inform you that your account on [Your Website Name] has been activated! You can now enjoy all the features and benefits of our platform.

                Thank you for choosing Cyber Appliance. We look forward to having you as an active member of our community.
                '''
                thread= threading.Thread(target=send_email,
                                        kwargs={
                                            'subject':'Your account with Cyber Appliance is now active!',
                                            'body':email_body,
                                            'sender':settings.BUSINESS_EMAIL,
                                            'recipients':[new_user.email],
                                            'fail_silently':False,
                                            'account_activation': True,
                                            'allow_html':True,
                                            'user_name':user_name
                                        })
                thread.start()

            

