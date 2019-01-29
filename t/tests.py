from django.test import TestCase
from t.models import *


# Create your tests here.
class JustTestCase(TestCase):
    # serialized_rollback = True

    # def test_refresh_from_db_behavior(self):
    #     H.objects.create(v=1000)
    #     h = H.objects.filter(v=1000).defer('v').first()
    #     self.assertEqual(h.v, 1000)

    def test_init_data_from_migrations(self):
        self.assertEqual(H.objects.count(), 2)
