$(function () {
    
    $('select[name="send_type"]').change(function(e){

        var show_container_id = $(this).find("option:selected").eq(0).attr('data-show-container');
        var subject_container = $('#subject_container').hide();

        $('form').bootstrapValidator('resetForm');

        subject_container.find('input,select').prop('disabled', true);

        if (show_container_id == 'subject_container') {
            subject_container.show().find('input,select').prop('disabled', false);
        }

    }).trigger('change');

});