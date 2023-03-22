/**
 * this file is for agreement_create/edit.html page
 *
 */

$(function(){

    var zone_obj = $("#drop_zone");
    var action_url = zone_obj.attr('data-url');
    var csrf_token = zone_obj.attr('data-token');

    Dropzone.autoDiscover = false;

    zone_obj.dropzone({

        url: action_url,
        autoProcessQueue : false,
        parallelUploads: 10,
        addRemoveLinks: true,
        dictResponseError: 'Error uploading file!',
        headers: {
            'X-CSRFToken': csrf_token
        },

        init : function() {

            var my_zone = this;

            $("#upload-btn").on("click", function () {
                var current_field_type = $('input[name="file_type"]');

                if (current_field_type.val() == '') {
                    JLib.small_box('File Upload Failed', 'Please select file type first', false);
                    return;
                }

                my_zone.processQueue();
            });

            $(".file-type-btn").click(function () {
                var btn_field_type = $(this).data('type');
                var current_field_type = $('input[name="file_type"]');

                if (btn_field_type == current_field_type.val()) {
                    return;
                }

                current_field_type.val(btn_field_type);

                $("#field-title").text($(this).data('title'));
                $('#file-notes').val('');
                my_zone.removeAllFiles(true);

                $("#dropzone-container").removeClass('hide');
                //my_zone.options.acceptedFiles = accept_file_type;
                //my_zone.hiddenFileInput.setAttribute("accept", accept_file_type);

            });

            this.on("error", function (file, errorMessage, xhr) {
                alert(errorMessage);
            });

            this.on("success", function (file, rep) {

                var real_form = $("#real-frm");

                if (rep.status != 'success') {
                    JLib.small_box('File Upload Failed', rep.err_msg, false);
                    return;
                }

                /**
                 * generate form
                 */
                var current_field = $('input[name="file_type"]').val();
                var hidden = $("<input></input>", {
                    'type': 'hidden',
                    'name': current_field,
                    'value': rep.file_name
                }).appendTo(real_form);

                /**
                 * delete old notes, and generate a new one
                 */
                var notes = $('#file-notes').val();
                var field_name = current_field + '_notes';

                $("input[name='" + field_name+ "']").remove();
                $("<input></input>", {
                    'type': 'hidden',
                    'name': field_name,
                    'value': notes
                }).appendTo(real_form);

                /**
                 * uploaded tag
                 */
                var container = "div[data-type='"+current_field+"']";
                $(container + ' > em').remove();
                $("<em></em>").appendTo($(container));
            });
        }

	});
});