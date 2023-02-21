# import re

# from django.forms import ValidationError
# from django.contrib.auth import get_user_model

# User = get_user_model()


# def returnUserName(email):
#     username = re.findall("\w*",email)[0]
#     if not User.objects.filter(username=username).exists():
#         return ValidationError("User already exist with this Username")
#     return username
