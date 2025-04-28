(function($) {
    $(document).ready(function() {
        var menuField = $('#id_menu');
        var parentField = $('#id_parent');

        function updateParentChoices() {
            var menuId = menuField.val();
            if (!menuId) {
                parentField.find('option').not('[value=""]').remove();
                return;
            }
            $.ajax({
                url: '/admin/menu/menuitem/parents/',
                data: {
                    'menu_id': menuId
                },
                success: function(data) {
                    parentField.find('option').not('[value=""]').remove();
                    $.each(data, function(index, item) {
                        var prefix = '';
                        for (var i = 0; i < item.level; i++) {
                            prefix += '--';
                        }
                        parentField.append(new Option(prefix + ' ' + item.title, item.id));
                    });
                }
            });
        }

        menuField.change(updateParentChoices);

        if (menuField.val()) {
            updateParentChoices();
        }
    });
})(django.jQuery);