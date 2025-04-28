from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Prefetch
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Menu(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, null=True)
    url = models.CharField(max_length=500, blank=True)

    class Meta:
        verbose_name = 'menu'
        verbose_name_plural = 'menus'

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        self.url = f'/menu/{slug}/'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MenuItem(MPTTModel):
    menu = models.ForeignKey(Menu, related_name='items',
                             on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    url = models.CharField(max_length=500, blank=True)

    class Meta:
        verbose_name = 'menu item'
        verbose_name_plural = 'menu items'
        unique_together = [['parent', 'title']]

    class MPTTMeta:
        order_insertion_by = ['order']

    # validate unique_together when parent is None and set self.url
    def clean(self):
        super().clean()

        try:
            self.menu
        except ObjectDoesNotExist:
            raise ValidationError({'menu': 'Menu is required'})

        if self.parent is None:
            qs = (
                MenuItem.objects
                .filter(menu=self.menu, title=self.title)
                .exclude(pk=self.pk)
            )
            if qs:
                raise ValidationError({
                    'title': (f'title {self.title} already exists '
                              f'on current level'),
                    'menu': (f'title {self.title} already exists '
                             f'on current level')
                })
        slug = slugify(self.title)
        parent_url = self.parent.url if self.parent else self.menu.url
        self.url = f'{parent_url}{slug}/'

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_children(self):
        if hasattr(self, '_children_cache'):
            return self._children_cache
        return super().get_children()

    def __str__(self):
        return self.title


@receiver([post_save, post_delete], sender=Menu)
@receiver([post_save, post_delete], sender=MenuItem)
def clear_menu_cache(sender, **kwargs):
    cache.delete('cached_menus')


def get_menu_cache():
    """Load all existing Menus with prefetched MenuItems and save to cache"""
    menus = cache.get('cached_menus')

    if not menus:
        menus = Menu.objects.prefetch_related(
            Prefetch('items',
                     queryset=MenuItem.objects.filter(parent__isnull=True)
                     .order_by('order')
                     .prefetch_related(
                         Prefetch('children',
                                  queryset=MenuItem.objects.all()
                                  .order_by('order'))
                     ),
                     to_attr='prepared_items')
        ).all()
        cache.set('cached_menus', menus, 86400)
    return menus
