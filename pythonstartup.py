"""python startup file for dj21 virtualenv"""

lines = [
    'from datetime import datetime, timedelta, date',
    'from django.db import models as models',
    'from django.utils import timezone as tz',
    'from django.db.models import Q, F, Case, Value, When, OuterRef, Subquery, Exists',
    'from django.db.models import Avg, Count, Max, Min, Sum, StdDev, Variance, Window',
    'from django.db.models.functions import CumeDist, DenseRank, FirstValue, Lag, LastValue, Lead, NthValue, Ntile, PercentRank, Rank, RowNumber',
    'from django.db.models.expressions import RawSQL',
    'from django.db import connection, connections, transaction',
    'from t.models import H, M, L, T, S, B, A, MI',
    'from shop.models import User, StatusGroup, OrderStatus, Order, OrderItem, Product, Manufacturer',
]

print('\n"{}" is executed due $PYTHONSTARTUP env'.format(__file__))
for line in lines:
    exec(line)
    print('>>> ' + line)
