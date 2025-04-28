from django import template

register = template.Library()


@register.inclusion_tag('menu/render_menu.html', takes_context=True)
def draw_menu(context, menu):
    request = context['request']
    current_url = request.path_info

    root_items = menu.prepared_items
    active_item = find_active_item(root_items, current_url)
    active_path = get_active_path(active_item)

    return {
        'root_items': root_items,
        'current_url': current_url,
        'active_path': active_path,
    }


def find_active_item(items, current_url):
    """Recursively find active element"""
    for item in items:
        if current_url.rstrip('/') == item.url.rstrip('/'):
            return item
        child = find_active_item(item.get_children(), current_url)
        if child:
            return child
    return None


def get_active_path(item):
    """Build elements list from root to active"""
    path = []
    while item:
        path.append(item.id)
        item = item.parent
    return path
