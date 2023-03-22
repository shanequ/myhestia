$(function () {
    
    var table_id = 'body';
    $(table_id).delegate( ".inactive-notification-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Inactivate Notification';
        var confirm_msg = 'Are you sure to inactivate this notification? Notification will <b class="txt-color-red">NOT</b> be sent anymore.';
        var ok_msg = 'Notification is inactivated.';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});

    $(table_id).delegate( ".active-notification-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Activate Notification';
        var confirm_msg = 'Are you sure to activate this notification?';
        var ok_msg = 'Notification is activated.';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});
    
});