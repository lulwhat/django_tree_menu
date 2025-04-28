from django.shortcuts import render
from django.views import View

from .models import get_menu_cache


class HomePageView(View):
    def get(self, request):
        menus = get_menu_cache()
        current_url = request.path_info

        return render(
            request,
            'home.html',
            {'menus': menus, 'current_url': current_url}
        )


class MenuDetailView(View):
    def get(self, request, url):
        menus = get_menu_cache()
        url_blocks = url.split('/')

        menu_url = f'/{url_blocks[0]}/{url_blocks[1]}/'
        menu = menus.filter(url=menu_url).first()

        return render(
            request,
            'menu/detail.html',
            {'menu': menu}
        )
