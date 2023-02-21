from django.test import TestCase

from nauvus.services.docusign.tokens import docusign_token


class TestDocusignToken(TestCase):
    def test_docusign_token_return_token(self):
        result = docusign_token()
        self.assertIsNotNone(result)

