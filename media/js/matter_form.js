$(function () {
    
    $("#matter-type").change(function(){

        var option = $("option:selected", this);
        var show_id = option.data('target-id');

        $('form').bootstrapValidator('resetForm');

        $('#other-container').hide().find('input,select').prop('disabled', true);
        $('#conveying-container').hide().find('input,select').prop('disabled', true);

        $('#'+show_id).show().find('input,select').prop('disabled', false);

    }).trigger('change');
    
});