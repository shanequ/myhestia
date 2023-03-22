$(function () {
    
    var table_id = 'body';
    $(table_id).delegate( ".inactive-client-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Inactivate Client';
        var confirm_msg = 'Are you sure to inactivate this client?';
        var ok_msg = 'Client is inactivated';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});

    $(table_id).delegate( ".active-client-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Activate Client';
        var confirm_msg = 'Are you sure to activate this client?';
        var ok_msg = 'Client is activated';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});

    $(table_id).delegate( ".delete-client-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Delete Client';
        var confirm_msg = 'Are you sure to delete this client?';
        var ok_msg = 'Client is deleted';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});
    
});