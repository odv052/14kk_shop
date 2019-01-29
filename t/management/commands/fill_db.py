from django.core.management import BaseCommand

from t.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        for h_i in range(2):
            h = H.objects.create(v=h_i)
            for m_i in range(2):
                m = M.objects.create(v=m_i, h=h)
                for l_i in range(3):
                    L.objects.create(v=l_i, m=m)
