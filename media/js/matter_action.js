$(function () {
    
    var table_id = 'body';
    $(table_id).delegate( ".close-matter-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Close Matter';
        var confirm_msg = 'Are you sure to close this matter? Notification will <b class="txt-color-red">NOT</b> be sent anymore.';
        var ok_msg = 'Matter is closed';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});

    $(table_id).delegate( ".active-matter-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Activate Matter';
        var confirm_msg = 'Are you sure to activate this matter? Inactive notification will <b class="txt-color-red">NOT</b> be activated automatically. ' +
            'Please review these notifications and activate them <b class="text-primary">manually</b>.';
        var ok_msg = 'Matter is activated';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});

    $(table_id).delegate( ".delete-matter-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Delete Matter';
        var confirm_msg = 'Are you sure to delete this matter? All related <b class="text-primary">notifications and documents</b> will be removed together.';
        var ok_msg = 'Matter is deleted';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});
    
    $(table_id).delegate( ".stamp-duty-paid-matter-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Change Matter Status To Stamp Duty Paid';
        var confirm_msg = 'Are you sure to change matter status to stamp duty paid? All stamp duty notifications will be <b class="text-primary">inactivated</b>.';
        var ok_msg = 'Matter status is changed';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});
    
});