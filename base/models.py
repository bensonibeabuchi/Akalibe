from django.db import models
from django.urls import reverse
import uuid
from users.models import CustomUser
from django.urls import reverse
from django.db.models import Avg


class Category(models.Model):
    category_name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    category_image = models.ImageField(
        upload_to='photos/categories', null=True, blank=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = ('Categories')

    def get_url(self):
            return reverse('products_by_category', args=[self.slug])



class Product(models.Model):
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product_name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_image = models.ImageField(upload_to='photos/products', null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    def get_url(self):
        return reverse('product-detail', args=[self.category.slug, self.slug])
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def save(self, *args, **kwargs):
        # Prevent stock from going below zero
        if self.stock < 0:
            self.stock = 0
        
        # Check if the product's stock was zero and now it's restocked
        if self.stock > 0 and not self.is_available:
            # If the stock is greater than zero and is_available is False,
            # set is_available to True
            self.is_available = True
        
        # Check if the product's stock is zero
        if self.stock == 0:
            # If stock is zero, set is_available to False
            self.is_available = False
        
        # Call the original save method to save the changes
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('product_name',)


class VariationManager(models.Manager):
    def colors(self):
        return self.filter(variation_category='color', is_active=True)

    def sizes(self):
        return self.filter(variation_category='size', is_active=True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=255, choices=(('color', 'Color'), ('size', 'Size')),)
    variation_value = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

    class Meta:
        ordering = ['product__product_name']


class Cart(models.Model):
    cart_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name

    def get_product_name(self):
        return self.product.product_name

    class Meta:
        ordering = ['product__product_name']


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField(blank=True)
    ip = models.CharField(max_length=255, blank=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject