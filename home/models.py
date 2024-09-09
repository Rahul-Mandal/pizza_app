from typing import Iterable
from django.db import models
import uuid
from django.contrib.auth.models import User
from django.db.models import Sum

# Create your models here.

class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now= True)

    class Meta:
        abstract = True

class PizzaCategory(BaseModel):
    category_name = models.CharField(max_length=100)

class Pizza(BaseModel):
    category = models.ForeignKey(PizzaCategory, on_delete=models.CASCADE, related_name='pizza1')
    pizza_name = models.CharField(max_length=100)
    price = models.IntegerField(default=100)
    images = models.ImageField(upload_to='pizza')

class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='carts')
    is_paid = models.BooleanField(default=False)
    instamojo_id = models.CharField(max_length=1000)
    
    def get_cart_total(self):
        return CartItems.objects.filter(cart = self).aggregate(Sum('pizza__price'))['pizza__price__sum']

class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_item')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)



# class Product(models.Model):
#     title = models.CharField(max_length=255)
#     sku = models.CharField(max_length=100, unique=True)
#     parent = models.ForeignKey('self', null=True, blank=True, related_name='variants', on_delete=
#                                models.SET_NULL)
#     is_active = models.BooleanField(default=True)
#     original_parent = models.ForeignKey('self', null=True, blank=True, related_name='original_variants', on_delete=models.SET_NULL)

#     def save(self, *args, **kwargs):
#         was_active = None
#         if self.pk:
#             was_active = Product.objects.get(pk=self.pk).is_active
#         super().save(*args, **kwargs)

#         #if there was a change in the active state, handle accoedingly

#         if was_active is not None and was_active != self.is_active:
#             if not self.is_active:
#                 self._handle_deactivation()
#             else:
#                 self._handle_activation()
    
#     def _handle_deactivation(self):
#         #Get all active children
#         active_children = self.variants.filter(is_active = True)
#         if active_children.exists():
#             # choose the first active child to be the new parent
#             new_parent = active_children.first()
#             new_parent.parent = new_parent
#             new_parent.save()

#             #Reassign all other children to the new parent

#             for child in active_children.exclude(pk=new_parent.pk):
#                 child.parent = new_parent
#                 child.save()
#     def _handle_activation(self):
#         #Reassign all children back to this product 
#         for child in self.variants.all():
#             child.parent = self
#             child.save()

#     def __str__(self):
#         return self.title

# class ParentLog(models.Model):
#     product = models.ForeignKey(Product, related_name='parent_logs', on_delete=models.CASCADE)
#     old_parent = models.ForeignKey(Product, related_name='old_parent_logs', null=True, blank=True, on_delete=models.SET_NULL)
#     new_parent = models.ForeignKey(Product, related_name='new_parent_logs', null=True, blank=True, on_delete=models.SET_NULL)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     @classmethod
#     def log_change(cls, product, new_parent, old_parent):
#         log_entry = cls(
#             product = product,
#             old_parent = old_parent,
#             new_parent = new_parent
#         )
#         log_entry.save()

#     def __str__(self) -> str:
#         return f"Product {self.product.id} parent change from {self.old_parent.id if self.old_parent else None} to "