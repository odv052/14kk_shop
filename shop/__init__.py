"""
Написать Viewset, который отображает список заказов.
Заказы должны быть отфильтрованы по группе статусов заказов, с которыми работает этот пользователь.
Опциональные фильтры:
1. Фильтр по общей стоимости заказа, включая цену доставки. Больше\меньше и одновременно использование
2. Фильтр заказов только по тем поставщикам, которые пользователь добавил в favorites
3. Фильтр по поставщику
4. Фильтр по продукту
5. Фильтр по заказам, в которых цена продажи не совпадает с ценой продукта
6. Фильтр по статусу

Сортировка.
1. По умолчанию отображать сначала самые новые заказы.
2. Дать возможность сортировки по времени создания заказа и по общей сумме.

В ответа должна быть выведена  структура заказа со вложенными объектами,
как в базе - OrderItem, OrderStatus

Написать unit tests

написать команду, которая сгенерит в базе:
1 миллион заказов
10 миллионов элементов корзины
3 миллиона продуктов
500 поставщиков
10 юзеров
3 статуса заказа (новые, в работе, закрыт)
2 группы статусов ( обрабатываются, завершены)

не должно быть проблемы N+1 запроса
Посмотреть как разные фильтры\сортировки влияют на скорость запроса.
"""