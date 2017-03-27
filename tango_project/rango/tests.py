from django.test import TestCase
from rango.models import Category


class CategoryMethodTests(TestCase):
    def test_slug_line_creation(self):
        cat = Category(name='Random Name', views=0, likes=0)
        cat.save()
        self.assertEqual(cat.slug, 'random-name')
