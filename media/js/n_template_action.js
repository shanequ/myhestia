$(function () {
    
    var table_id = 'table';
    $(table_id).delegate( ".inactive-template-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Inactivate Notification Template';
        var confirm_msg = 'Are you sure to inactivate this template? ' +
            'This template will <b class="txt-color-red">NOT</b> be used to generate notification anymore. ' +
            'Existing active notifications will still be sent out on scheduled time.';
        var ok_msg = 'Template is inactivated.';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});

    $(table_id).delegate( ".active-template-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Activate Notification Template';
        var confirm_msg = 'Are you sure to activate this template?';
        var ok_msg = 'Template is activated.';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});

});