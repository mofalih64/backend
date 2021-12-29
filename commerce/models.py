import uuid

from PIL import Image
from django.contrib.auth import get_user_model
from django.db import models
from mptt.fields import TreeForeignKey
from simple_history.models import HistoricalRecords

from config.utils.models import Entity

User = get_user_model()


class Product(Entity):
    name = models.CharField(verbose_name='name', max_length=255)
    image = models.CharField(verbose_name='image', max_length=255)
    description = models.TextField('description', null=True, blank=True)

    price = models.DecimalField('price', max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField('discounted price', max_digits=10, decimal_places=2)
    type = models.ForeignKey('commerce.Type', verbose_name='type', related_name='products',
                             on_delete=models.SET_NULL,
                             null=True, blank=True)
    vendor = models.ForeignKey('commerce.Vendor', verbose_name='vendor', related_name='products',
                               on_delete=models.SET_NULL,
                               null=True, blank=True)
    category = models.ForeignKey('commerce.Category', verbose_name='category', related_name='products',
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)
    popular = models.BooleanField('is popular',default=False)
    best_seller = models.BooleanField('is best seller',default=False)
    quantity = models.IntegerField('quantity')

    def __str__(self):
        return self.name


class Order(Entity):
    user = models.ForeignKey(User, verbose_name='user', related_name='orders', null=True, blank=True,
                             on_delete=models.CASCADE)
    total = models.DecimalField('total', blank=True, null=True, max_digits=1000, decimal_places=0)


    note = models.CharField('note', null=True, blank=True, max_length=255)
    ref_code = models.CharField('ref code', max_length=255)
    ordered = models.BooleanField('ordered')
    items = models.ManyToManyField('commerce.Item', verbose_name='items', related_name='order')

    def __str__(self):
        return f'{self.user.first_name} + {self.total}'

    @property
    def order_total(self):
        return sum(
            i.product.discounted_price * i.item_qty for i in self.items.all()
        )


class Item(Entity):
    """
    Product can live alone in the system, while
    Item can only live within an order
    """
    user = models.ForeignKey(User, verbose_name='user', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('commerce.Product', verbose_name='product',
                                on_delete=models.CASCADE)
    item_qty = models.IntegerField('item_qty')
    ordered = models.BooleanField('ordered', default=False)

    def __str__(self):
        return self.product.name


class Wish_list(Entity):
    user = models.ForeignKey(User, verbose_name='user', related_name='wishes', on_delete=models.CASCADE)
    product = models.ForeignKey('commerce.Product', verbose_name='product',
                                on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name





class Category(Entity):
    name = models.CharField('name', max_length=255)

    is_active = models.BooleanField('is active')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class Type(Entity):
    name = models.CharField('name', max_length=225)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):
        super().save(*args, **kwargs)


class Vendor(Entity):
    name = models.CharField('name', max_length=255)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):
        super().save(*args, **kwargs)
