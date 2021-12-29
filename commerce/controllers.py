import random
import string
from typing import List

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from account.authorization import GlobalAuth
from commerce.models import Product, Category, Vendor, Item, Order, Wish_list
from commerce.schemas import ProductOut, VendorOut, ItemOut, ItemSchema, ItemCreate, CategoryOut, WishesCreate, \
    WishesOut, OrderOut
from config.utils.schemas import MessageOut

products_controller = Router(tags=['products'])
address_controller = Router(tags=['addresses'])
vendor_controller = Router(tags=['vendors'])
order_controller = Router(tags=['orders'])
wishes_controller = Router(tags=['wish list'])

User = get_user_model()


@products_controller.get('', summary='List all products', response={
    200: List[ProductOut],
    404: MessageOut
})
def list_products(
        request, *,
        q: str = None,
        popular: bool = None,
        best_seller: bool = None,
        vendor=None,
        type=None,
        category=None,
):
    """
    To create an order please provide:
     - **first_name**
     - **last_name**
     - and **list of Items** *(product + amount)*
    """
    products_qs = Product.objects.all() \
        .select_related('vendor', 'category', )

    if not products_qs:
        return 404, {'detail': 'No products found'}

    if q:
        products_qs = products_qs.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )

    if popular:
        products_qs = products_qs.filter(popular=popular)

    if best_seller:
        products_qs = products_qs.filter(best_seller=best_seller)

    if vendor:
        products_qs = products_qs.filter(vendor__name=vendor)

    if type:
        products_qs = products_qs.filter(type__name=type)

    if category:
        products_qs = products_qs.filter(category__name=category)

    return products_qs


"""
# product = Product.objects.all().select_related('merchant', 'category', 'vendor', 'label')
    # print(product)
    #
    # order = Product.objects.all().select_related('address', 'user').prefetch_related('items')

    # try:
    #     one_product = Product.objects.get(id='8d3dd0f1-2910-457c-89e3-1b0ed6aa720a')
    # except Product.DoesNotExist:
    #     return {"detail": "Not found"}
    # print(one_product)
    #
    # shortcut_function = get_object_or_404(Product, id='8d3dd0f1-2910-457c-89e3-1b0ed6aa720a')
    # print(shortcut_function)

    # print(type(product))
    # print(product.merchant.name)
    # print(type(product.merchant))
    # print(type(product.category))


Product <- Merchant, Label, Category, Vendor

Retrieve 1000 Products form DB

products = Product.objects.all()[:1000] (select * from product limit 1000)

for p in products:
    print(p)
    
for every product, we retrieve (Merchant, Label, Category, Vendor) records

Merchant.objects.get(id=p.merchant_id) (select * from merchant where id = 'p.merchant_id')
Label.objects.get(id=p.label_id) (select * from merchant where id = 'p.label_id')
Category.objects.get(id=p.category_id) (select * from merchant where id = 'p.category_id')
Vendor.objects.get(id=p.vendor_id) (select * from merchant where id = 'p.vendor_id')

4*1000+1

Solution: Eager loading

products = (select * from product limit 1000)

mids = [p1.merchant_id, p2.merchant_id, ...]
[p1.label_id, p2.label_id, ...]
.
.
.

select * from merchant where id in (mids) * 4 for (label, category and vendor)

4+1

"""


@products_controller.get('/{id}', response={
    200: ProductOut,
})
def return_product(request, id):
    product = get_object_or_404(Product, id=id)
    return product


@wishes_controller.get('wishes list', auth=GlobalAuth(), response={
    200: List[WishesOut],
    404: MessageOut
})
def view_WishesList(request):
    user = User.objects.get(id=request.auth['pk'])
    wishes_items = Wish_list.objects.filter(user=user)

    if wishes_items:
        return wishes_items

    return 404, {'detail': 'Your wishes list is empty!'}


@wishes_controller.post('add-to-wishes', auth=GlobalAuth(), response={
    200: MessageOut,
    400: MessageOut
})
def add_update_wishes(request, wishes_in: WishesCreate):

    user = User.objects.get(id=request.auth['pk'])

    product = get_object_or_404(Product,id=wishes_in.product_id)
    wish = Wish_list.objects.get_or_create(product=product,user=user)

    #Wish_list.objects.create(**wishes_in.dict(), user=user)

    return 200, {'detail': 'Added to wish list successfully'}

@wishes_controller.delete('wish/{id}', auth=GlobalAuth(), response={
    204: MessageOut
})
def delete_wish(request, id: UUID4):
    user = User.objects.get(id=request.auth['pk'])
    wish = get_object_or_404(Wish_list, id=id, user=user)
    wish.delete()

    return 204, {'detail': 'wish deleted!'}


@order_controller.get('cart', auth=GlobalAuth(), response={
    200: List[ItemOut],
    404: MessageOut
})
def view_cart(request):
    uesr = User.objects.get(id=request.auth['pk'])
    cart_items = Item.objects.filter(user=uesr, ordered=False)

    if cart_items:
        return cart_items

    return 404, {'detail': 'Your cart is empty, go shop like crazy!'}


@order_controller.post('add-to-cart', auth=GlobalAuth(), response={
    200: MessageOut,
    # 400: MessageOut
})
def add_update_cart(request, item_in: ItemCreate):
    try:
        user = User.objects.get(id=request.auth['pk'])
        item = Item.objects.get(product_id=item_in.product_id, user=user)
        item.item_qty += 1
        item.save()
    except Item.DoesNotExist:
        Item.objects.create(**item_in.dict(), user=user)

    return 200, {'detail': 'Added to cart successfully'}


@order_controller.post('item/{id}/reduce-quantity', auth=GlobalAuth(), response={
    200: MessageOut,
})
def reduce_item_quantity(request, id: UUID4):
    user = User.objects.get(id=request.auth['pk'])
    item = get_object_or_404(Item, id=id, user=user)
    if item.item_qty <= 1:
        item.delete()
        return 200, {'detail': 'Item deleted!'}
    item.item_qty -= 1
    item.save()

    return 200, {'detail': 'Item quantity reduced successfully!'}


@order_controller.delete('item/{id}', auth=GlobalAuth(), response={
    204: MessageOut
})
def delete_item(request, id: UUID4):
    user = User.objects.get(id=request.auth['pk'])
    item = get_object_or_404(Item, id=id, user=user)
    item.delete()

    return 204, {'detail': 'Item deleted!'}


def generate_ref_code():
    return ''.join(random.sample(string.ascii_letters + string.digits, 6))


@order_controller.post('create-order', auth=GlobalAuth(), response=MessageOut)
def create_order(request):
    '''
    * add items and mark (ordered) field as True
    * add ref_number

    * calculate the total
    '''
    user = User.objects.get(id=request.auth['pk'])
    order_qs = Order.objects.create(
        user=user,

        ref_code=generate_ref_code(),
        ordered=False,
    )

    user_items = Item.objects.filter(user=user).filter(ordered=False)

    order_qs.items.add(*user_items)
    order_qs.total = order_qs.order_total
    user_items.update(ordered=True)
    order_qs.save()

    return {'detail': 'order created successfully'}

@order_controller.get('list_orders',auth=GlobalAuth(),response={
    200:List[OrderOut],
})
def get_orders(request):
    user = User.objects.get(id=request.auth['pk'])
    orders = Order.objects.filter(user=user)
    return orders