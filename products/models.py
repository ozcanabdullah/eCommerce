import os
import random

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.urls import reverse

from ecommerce.utils import unique_slug_generator


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1, 9999999999)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return f'products/{new_filename}/{final_filename}'


class ProductQuerySet(models.query.QuerySet):  # Custom queryset
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
        lookups = (Q(title__icontains=query) |
                   Q(description__icontains=query) |
                   Q(price__icontains=query) |
                   Q(tag__title__icontains=query)
                   )
        return self.filter(lookups).distinct()


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self):
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)  # Product.objects.self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)


class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=19, default=39.99)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_digital = models.BooleanField(default=False)

    objects = ProductManager()

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title

    # For python 2
    # def __unicode__(self):
    #     return self.title


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver, sender=Product)


def upload_product_file_location(instance, filename):
    print(instance.id)
    slug = instance.product.slug
    if not slug:
        slug = unique_slug_generator(instance.product)
    location = f'product/{slug}/'
    return location + filename  # 'path/to/filename.mp3'


class ProductFile(models.Model):
    product = models.ForeignKey(Product)
    file = models.FileField(
        upload_to=upload_product_file_location,
        storage=FileSystemStorage(location=settings.PROTECTED_ROOT)
    )

    def __str__(self):
        return str(self.file.name)
