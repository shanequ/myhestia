$(function () {
    
    var table_id = 'body';
    $(table_id).delegate( ".delete-project-btn", "click", function(e) {

        e.preventDefault();

        var data_url = $(this).attr('data-url');
        if (data_url == '') {
            return;
        }

        var title = 'Delete Project';
        var confirm_msg = 'Are you sure to delete this project?';
        var ok_msg = 'Project is deleted';

        JLib.send_simple_ajax_action(data_url, title, confirm_msg, ok_msg, {});
	});

});