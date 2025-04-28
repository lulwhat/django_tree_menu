from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.http import JsonResponse

from .models import Menu, MenuItem


class MenuItemForm(ModelForm):
    class Meta:
        model = MenuItem
        fields = '__all__'

    def clean(self):
        cleaned_data = {}
        try:
            cleaned_data = super().clean()
            for field, value in cleaned_data.items():
                setattr(self.instance, field, value)
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                for field, error in e.error_dict.items():
                    self.add_error(field, error)
            else:
                for error in e.error_list:
                    self.add_error(None, error)
        return cleaned_data


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ['title', 'parent', 'order']
    readonly_fields = ('url',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                kwargs["queryset"] = MenuItem.objects.filter(menu_id=obj_id)
            else:
                kwargs["queryset"] = MenuItem.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    readonly_fields = ('url',)

    def get_inlines(self, request, obj):
        if obj:
            return [MenuItemInline]
        return []


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'menu', 'parent', 'order']
    list_filter = ['menu']
    search_fields = ['title']
    readonly_fields = ('url',)
    form = MenuItemForm

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            'admin/menuitem.js',
        )

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('parents/', self.admin_site.admin_view(self.get_parents),
                 name='menuitem-parents')
        ]
        return custom_urls + urls

    def get_parents(self, request):
        menu_id = request.GET.get('menu_id')
        if not menu_id:
            return JsonResponse([], safe=False)
        items = MenuItem.objects.filter(
            menu_id=menu_id
        ).order_by('tree_id', 'lft')
        data = [
            {'id': item.pk,
             'title': item.title,
             'level': item.get_level()
             } for item in items
        ]
        return JsonResponse(data, safe=False)
