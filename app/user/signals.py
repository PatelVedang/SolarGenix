from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from user.models import User
import threading
from utils.email import send_email
from django.conf import settings
import uuid
import os

# def create_letter_image(initials, image_path):

#     # Create an image with a red background
#     width, height = 100, 100
#     image = Image.new("RGB", (width, height), "red")

#     # Use a basic font (change the font path to a font on your system)
#     font_path = f'{settings.BASE_DIR}/static/fonts/gargi.ttf'
#     font_size = 40
#     font = ImageFont.truetype(font_path, font_size)

#     # Create a drawing context
#     draw = ImageDraw.Draw(image)

#     # Use textbbox to get the bounding box of the text
#     text_bbox = draw.textbbox((0, 0), initials, font=font)

#     # Calculate the position to center the letter
#     x = (width - text_bbox[2] - text_bbox[0]) // 2
#     y = (height - text_bbox[3] - text_bbox[1]) // 2

#     # Draw the letter in the center of the image with white font
#     draw.text((x, y), initials, font=font, fill="white")

#     # Save the image to a file
#     image.save(image_path)

# def make_path(target_path):
#     sub_path = target_path.replace(str(settings.BASE_DIR), '')
#     sub_path_content = sub_path.split("/")
#     for index in range(len(sub_path_content)):
#         path = f'{settings.BASE_DIR}{"/".join(sub_path_content[:index+1])}'
#         if not os.path.exists(path):
#             os.mkdir(path)

# @receiver(pre_save, sender=User)
# def user_verify_signal(sender, instance, **kwargs):
#     # Only on update method 
#     if not instance._state.adding:
#         # Getting old record
#         old_user = User.objects.get(email=instance.email)
        
#         # Getting updated record
#         new_user = instance

#         # old_is_verified = old_user.is_verified
#         # new_is_verified = new_user.is_verified
#         # if old_is_verified != new_is_verified:
#         #     # If the status of is_verified is change to True from False
#         #     if new_is_verified:

#         #         # Sending the user account activation mail to end_user
#         #         user_name = f"{new_user.first_name} {new_user.last_name}".upper()
#         #         email_body =  f'''
#         #         Dear {user_name},

#         #         We're excited to inform you that your account on Cyber Appliance has been activated! You can now enjoy all the features and benefits of our platform.

#         #         Thank you for choosing Cyber Appliance. We look forward to having you as an active member of our community.
#         #         '''
#         #         thread= threading.Thread(target=send_email,
#         #                                 kwargs={
#         #                                     'subject':'Your account with Cyber Appliance is now active!',
#         #                                     'body':email_body,
#         #                                     'sender':settings.BUSINESS_EMAIL,
#         #                                     'recipients':[new_user.email],
#         #                                     'user_name':user_name,
#         #                                     'html_template':'account-activation.html'
#         #                                 })
#         #         thread.start()

#         if old_user.profile_image and new_user.profile_image and old_user.profile_image != new_user.profile_image:
#             profile_path= f'{settings.MEDIA_ROOT}{str(old_user.profile_image)}'

#             if os.path.exists(profile_path):
#                 if os.path.isfile(profile_path):
#                     os.remove(profile_path)

#         # if old_user.profile_image and new_user.profile_image


# @receiver(post_save, sender=User)
# def create_profile_image(sender, instance, created, **kwargs):
#     # Save user initial letter as profile image on save method
#     if instance._state.adding or not instance.profile_image:
#         initials = f"{instance.first_name[0]}{instance.last_name[0]}".upper()
#         relative_profile_folder_path = f"user_initial/{instance.id}"
#         file_name = f'{uuid.uuid4()}.png'
#         profile_folder_path = f"{settings.MEDIA_ROOT}{relative_profile_folder_path}"
#         make_path(profile_folder_path)
#         create_letter_image(initials, f'{profile_folder_path}/{file_name}')
#         instance.profile_image = f'{relative_profile_folder_path}/{file_name}'
#         instance.save()
    
#     if not instance.stripe_customer_id:

#         customer = stripe.Customer.create(
#             email=instance.email,
#             phone=instance.mobile_number,
#             name=f"{instance.first_name} {instance.last_name}"
#         )
#         # Save the Stripe customer ID to your user model
#         instance.stripe_customer_id = customer.id
#         instance.save()

            

