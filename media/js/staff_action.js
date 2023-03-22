$(function () {
    
    /**
     * active / inactive user
     */
    var table_id = 'body';
    $(table_id).delegate(".inactive-user-btn", "click", function(e) {

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Inactivate Staff';
        var confirm_msg = 'Are you sure to inactivate this staff? Staff <b class="txt-color-red">CANNOT</b> login system anymore.';
        var ok_msg = 'Staff is inactivated';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});

        e.preventDefault();
	});

    $(table_id).delegate(".active-user-btn", "click", function(e) {

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Activate Staff';
        var confirm_msg = 'Are you sure to activate this staff?';
        var ok_msg = 'Staff is activated';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});

        e.preventDefault();
	});
    
    $(table_id).delegate(".delete-user-btn", "click", function(e) {

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Delete Staff';
        var confirm_msg = 'Are you sure to delete this staff?';
        var ok_msg = 'Staff is deleted';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});

        e.preventDefault();
	});
    
});