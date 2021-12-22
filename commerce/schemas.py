from typing import List

from ninja import ModelSchema, Schema
from ninja.orm import create_schema
from pydantic import UUID4

from commerce.models import Product


class UUIDSchema(Schema):
    id: UUID4


# ProductSchemaOut = create_schema(Product, depth=2)

class VendorOut(UUIDSchema):
    name: str


class CategoryOut(UUIDSchema):
    name: str


CategoryOut.update_forward_refs()


class ProductOut(ModelSchema):
    vendor: VendorOut

    category: CategoryOut

    class Config:
        model = Product
        model_fields = ['id',
                        'name',
                        'image',
                        'description',
                        'weight',
                        'length',
                        'width',
                        'height',
                        'on_charge',
                        'price',
                        'discounted_price',
                        'vendor',
                        'category',

                        ]


# class ProductManualSchemaOut(Schema):
#     pass


class WishesSchema(Schema):
    product: ProductOut

class WishesCreate(Schema):
    product_id:UUID4

class WishesOut(UUIDSchema,WishesSchema):
    pass






class ItemSchema(Schema):
    # user:
    product: ProductOut
    item_qty: int
    ordered: bool


class ItemCreate(Schema):
    product_id: UUID4
    item_qty: int


class ItemOut(UUIDSchema, ItemSchema):
    pass
