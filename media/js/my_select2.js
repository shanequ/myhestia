/**
 * This file is for generating select2
 */
var JLib = window.JLib || {};


JLib.simple_select2 = function(selector, multiple, width) {

    width = width || '350px';
    multiple = multiple || false;

    var action_url = $(selector).attr('data-url');

    $(selector).select2({
        allowClear: true,
        multiple: multiple,
        width: width,
        initSelection : function (element, callback) {
            var data = [];
            var ids = $.parseJSON(element.val());
            if (ids !== "") {
                $.ajax(action_url, {
                    data: {ids: ids},
                    dataType: "json"
                }).done(function (ret) {
                    $.each(ret.items, function (i, value) {
                        data.push({id: value.id, text: value.text});
                    });

                    if (data.length > 0) {
                        callback(data);
                    }
                });
            }
        },
        ajax: {
            url: action_url,
            dataType: 'json',
            delay: 250,
            data: function(term, page) {
                return {
                    term: term,
                    page: page
                };
            },
            results: function (data, page) {
              // parse the results into the format expected by Select2.
              // since we are using custom formatting functions we do not need to
              // alter the remote JSON data
              return {
                  results: data.items,
                  more: data.has_more
              };
            },
            cache: true
        }
    });
};