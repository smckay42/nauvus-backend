from django.core.validators import RegexValidator


class ZipCodeValidator(RegexValidator):
    regex = r"^[0-9]{5}(?:-[0-9]{4})?$"
    message = "Invalid ZipCode."
