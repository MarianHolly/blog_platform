from django.test import TestCase

from engagement.forms import CommentModelForm


class CommentFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nCommentFormTest - setting setUpTestData')

    def test_form_valid_data(self):
        form = CommentModelForm(data={'content': 'Test comment content'})
        self.assertTrue(form.is_valid())

    def test_form_empty_content(self):
        form = CommentModelForm(data={'content': ''})
        self.assertFalse(form.is_valid())

    def test_form_too_long_content(self):
        form = CommentModelForm(data={'content': 'a' * 501})
        self.assertFalse(form.is_valid())