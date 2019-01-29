import datetime
from random import randint

from django.core.management import BaseCommand, call_command
from django.db import connection

from shop.models import User, StatusGroup, OrderStatus, Order, OrderItem, Product, Manufacturer

# написать команду, которая сгенерит в базе:
# 1 миллион заказов
# 10 миллионов элементов корзины
# 3 миллиона продуктов
# 500 поставщиков
# 10 юзеров
# 3 статуса заказа (новые, в работе, закрыт)
# 2 группы статусов ( обрабатываются, завершены)
COUNT = {
    'Order': 10 ** 6,
    'OrderItems': 10 ** 7,
    'Product': 3 * 10 ** 6,
}


def speed_up_generate_sql(cursor, table_name, sql):
    # disable index
    cursor.execute('UPDATE pg_index '
                   'SET indisready=false '
                   'WHERE indrelid = ('
                   'SELECT oid '
                   'FROM pg_class '
                   "WHERE relname='{}'"
                   ')'.format(table_name))
    # disable triggers
    cursor.execute('ALTER TABLE {} DISABLE TRIGGER ALL'.format(table_name))

    cursor.execute(sql)

    # enable triggers
    cursor.execute('ALTER TABLE {} ENABLE TRIGGER ALL'.format(table_name))
    # enable index
    cursor.execute('UPDATE pg_index '
                   'SET indisready=true '
                   'WHERE indrelid = ('
                   'SELECT oid '
                   'FROM pg_class '
                   "WHERE relname='{}'"
                   ')'.format(table_name))
    # reindex
    cursor.execute('REINDEX TABLE {};'.format(table_name))


class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command('flush')

        start_time = datetime.datetime.now()
        st_group_in_process = StatusGroup.objects.create(name='in process')
        st_group_finished = StatusGroup.objects.create(name='finished')

        OrderStatus.objects.create(name='new', group=st_group_in_process)
        OrderStatus.objects.create(name='in work', group=st_group_in_process)
        OrderStatus.objects.create(name='closed', group=st_group_finished)

        with connection.cursor() as cursor:
            # generate Manufacturers
            speed_up_generate_sql(
                cursor,
                table_name=Manufacturer._meta.db_table,
                sql='INSERT INTO {} (id, name) VALUES ('
                               'generate_series(1,500), '
                               'left(md5(random()::text), 15)'
                               ')'.format(Manufacturer._meta.db_table),
            )

            # generate Products
            speed_up_generate_sql(
                cursor,
                table_name=Product._meta.db_table,
                sql='INSERT INTO {table} (id, sku, price, manufacturer_id) VALUES ('
                               'generate_series(1, ({product_number})::int), '
                               'concat(md5(random()::text), md5(random()::text)), '
                               '(random() * 1000)::int, '
                               'trunc(random() * 500) + 1'
                               ')'.format(
                    table=Product._meta.db_table,
                    product_number=COUNT['Product'])
            )

            # generate Orders
            speed_up_generate_sql(
                cursor,
                table_name=Order._meta.db_table,
                sql='INSERT INTO {table} (id, created, number, delivery_price, status_id) VALUES ('
                               'generate_series(1, ({order_number})::int), '
                               "date '2017-01-10' + (random()*365)::int, "
                               'concat(md5(random()::text), md5(random()::text)), '
                               '(random() * 100)::int, '
                               'trunc(random() * 3) + 1'
                               ')'.format(
                    table=Order._meta.db_table,
                    order_number=COUNT['Order'], )
            )

            # OrderItems
            speed_up_generate_sql(
                cursor,
                table_name=OrderItem._meta.db_table,
                sql='INSERT INTO {table} (id, created, price, order_id, product_id) VALUES ('
                    'generate_series(1, ({orderitem_number})::int), '
                    "date '2018-01-10' + (random()*365)::int, "
                    '0, '
                    'trunc(random() * {order_number}) + 1, '
                    'trunc(random() * {product_number}) + 1'
                    ')'.format(
                        table=OrderItem._meta.db_table,
                        orderitem_number=COUNT['OrderItems'],
                        order_number=COUNT['Order'],
                        product_number=COUNT['Product'], )
            )

            # fix price in OrderItem - Product
            speed_up_generate_sql(
                cursor,
                table_name=OrderItem._meta.db_table,
                sql='UPDATE {order_table} '
                    'SET price={product_table}.price '
                    'FROM {product_table} '
                    'WHERE {order_table}.product_id={product_table}.id'.format(
                        order_table=OrderItem._meta.db_table,
                        product_table=Product._meta.db_table,
                    )
            )

            # change price for random 100k rows
            speed_up_generate_sql(
                cursor,
                table_name=OrderItem._meta.db_table,
                sql='UPDATE {table} '
                    'SET price = price + trunc(random() * 40) '
                    'WHERE id IN (SELECT id FROM {table} ORDER BY random() limit 100000);'.format(
                        table=OrderItem._meta.db_table,
                    )
            )

            # remove rows violate unique together constraint on order_id, product_id
            cursor.execute('WITH u AS'
                           '(SELECT DISTINCT ON (order_id, product_id) id FROM {table})'
                           'DELETE FROM {table} WHERE {table}.id NOT IN (SELECT id FROM u)'.format(
                table=OrderItem._meta.db_table
            ))

            # populate Order total_price
            speed_up_generate_sql(
                cursor,
                table_name=Order._meta.db_table,
                sql='UPDATE {order_table} O '
                    'SET total_price = '
                    'coalesce((SELECT SUM(price) FROM {orderitem_table} I WHERE I.order_id=O.id), 0) '
                    '+ O.delivery_price'.format(
                    order_table=Order._meta.db_table,
                    orderitem_table=Order._meta.db_table,
                )
            )

        # Users
        for i in range(10):
            user = User.objects.create()
            user.favorite_manufactures.set([randint(1, 500) for _ in range(randint(1, 10))])
            user.allowed_groups.set([randint(1, 2) for _ in range(randint(1, 2))])

        total_sec = (datetime.datetime.now() - start_time).total_seconds()
        self.stdout.write('DB populating time: {}'.format(str(total_sec)))