$(function () {
    
    $('#send_type').change(function(e){

        var option = $("option:selected", this);
        var show_id = option.data('target-id');

        $('form').bootstrapValidator('resetForm');

        $('#email-container').hide().find('input,select,textarea').prop('disabled', true);
        $('#sms-container').hide().find('input,select,textarea').prop('disabled', true);

        $('#'+show_id).show().find('input,select,textarea').prop('disabled', false);

    }).trigger('change');

});