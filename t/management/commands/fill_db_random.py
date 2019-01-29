import random
from datetime import datetime, date, timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from t.models import *


class Command(BaseCommand):
    output_transaction = True

    def handle(self, *args, **options):
        # H, M, L
        for h_i in range(random.randint(2, 10)):
            h = H.objects.create(v=random.randint(0, 50))
            for m_i in range(random.randint(2, 15)):
                m = M.objects.create(v=random.randint(0, 50), h=h)
                for l_i in range(random.randint(2, 40)):
                    L.objects.create(v=random.randint(0, 100), m=m)

        # T
        now = timezone.now()
        for _ in range(random.randint(3, 15)):
            days = random.randint(1, 365)
            start = now - timedelta(days=days * 2)
            end = start + timedelta(days=random.randint(1, days))
            T.objects.create(
                v=random.randint(0, 100),
                start=start,
                end=end,
            )

        # S, A, B
        s = [S.objects.create(v=random.randint(0, 100)) for _ in range(random.randint(5, 15))]
        a = [A.objects.create(v=random.randint(0, 100)) for _ in range(random.randint(5, 15))]
        for _ in range(random.randint(len(s)+len(a), len(s)*len(a))):
            b = B.objects.create(
                v=random.randint(0, 100),
            )
            random.shuffle(s)
            random.shuffle(a)
            b.s.set(s[1:random.randint(2, len(s))])
            b.a.set(a[1:random.randint(2, len(a))])
