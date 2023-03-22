/**
 * This file is for common function and global init
 */
var JLib = window.JLib || {};
/**
 * global init
 */
var map;
$(function() {
    /**
     * date picker
     */
    $(".my-date-picker").datepicker({
        format: 'dd-mm-yyyy',
        autoclose: true,
        todayHighlight: true,
        minView: 2,
        viewSelect: 2,
        container: "#main"
    });

    /**
     * datetime picker
     */
    $(".my-datetime-picker").datetimepicker({
        format: 'dd-mm-yyyy hh:ii',
        autoclose: true,
        todayHighlight: true,
        startView: 2,
        minuteStep: 30
    });

    /**
     * summer note
     */
    $('.my-summernote').summernote({
        height: 300,
        toolbar: [
            ['style', ['style']],
            ['font', ['bold', 'italic', 'underline', 'clear']],
            ['fontname', ['fontname', 'fontsize']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['height', ['height']],
            ['insert', ['link', 'video', 'hr', 'table']],
            ['view', ['fullscreen', 'codeview']],
            ['help', ['help']]
        ]
    });

    /**
     * mask money.
     */
    $('.mask-money').autoNumeric('init', {
        vMin: '0.00',
        aSign: '$'
    });
    $('.mask-amount').autoNumeric('init');

    // get real value for form submit
    $('form').submit(function(){

        $('.mask-money, .mask-amount').each(function(i){
            var self = $(this);
            try{
                var v = self.autoNumeric('get');
                // self.autoNumeric('destroy');
                self.val(v);
            } catch(err){}
        });

        $('.my-summernote').each(function(i) {
            var self = $(this);
            try{
                var html_text = self.summernote('code');
                var v = self.html(html_text);
            } catch(err){}
        });
    });

    $(".async-img").each(function(k, item) {
        var container = $(this);
        var img_url = $(this).attr('data-url');
        var img_width = $(this).attr('data-width');
        var img = $("<img />", {'src': img_url, 'width': img_width, 'class': 'mt5'}).on('load', function() {
            if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) {
                // alert('broken image!');
            } else {
                container.append(img);
            }
        });
    });

    /* init jquery autocomplete */
    $(".autocomplete").autocomplete({
        minLength: 0,
        scroll: true
    }).focus(function() {
        $(this).autocomplete("search", "");
    });
});


/**
 * popup small box
 *
 * @param title
 * @param content
 * @param is_succ - for different color.
 */
JLib.small_box = function (title, content, is_succ) {

    // green or red
    var time_out = 20000;
    var color = "#C46A69";
    if (is_succ) {
        time_out = 4000;
        color = "#659265";
    }

    $.smallBox({
        title : title,
        content : "<i class='fa fa-clock-o'></i> <i>" + content + "</i>",
        color : color,
        iconSmall : "fa fa-check fa-2x fadeInRight animated",
        timeout : time_out
    });
};

/**
 * Send simple ajax post request, and confirm dialog will be shown
 *
 * @param action_url    - ajax url
 * @param title         - confirm dialog title
 * @param confirm_msg   - confirm message
 * @param ok_msg      - successful message if server responses OK
 * @param data - post data
 */
JLib.send_simple_ajax_action = function (action_url, title, confirm_msg, ok_msg, data) {

    if (action_url == '' || title == '' || confirm_msg == '') {
        return;
    }

    data = data || {};

    var ok_message = ok_msg || title + ' Successfully';

    $.SmartMessageBox({
        title : title,
        content : confirm_msg,
        buttons : '[No][Yes]'

    }, function(ButtonPressed) {

        if (ButtonPressed === "No") {
            return;
        }

        $.ajax({
            url : action_url,
            type : 'post',
            dataType : 'json',
            data : data,
            success : function(rep) {
                if(rep.status == 'error') {
                    JLib.small_box(title + ' Failed!', rep.message, false);
                    return;
                }
                /**
                 * if successfully,
                 * show message box and redirect to index page
                 */
                JLib.small_box(title + ' Successfully!', ok_message, true);

                var redirect_url = rep.next;
                redirect_url == '' || typeof redirect_url == 'undefined' ?
                    window.location.reload() :
                    window.location.href = redirect_url;

            } // /success
        }); // /ajax

    });

};

/**
 * initial JQuery Drop zone. http://www.dropzonejs.com/
 *
 * @param zone_id
 * @param file_types - accepted file types, Eg.: 'image/*,application/pdf,.psd'
 * @param real_frm_id - form id to be submitted
 * @param hidden_field_name - form field name to be submitted
 */
JLib.init_drop_zone = function (zone_id, real_frm_id, hidden_field_name, file_types, max_files) {

    file_types = file_types || '';
    max_files = max_files || null;

    if (zone_id == '' || real_frm_id == '' || hidden_field_name == '') {
        return;
    }

    var zone_obj = $("#" + zone_id);
    var action_url = zone_obj.attr('data-url');
    var csrf_token = zone_obj.attr('data-token');

    Dropzone.autoDiscover = false;

    zone_obj.dropzone({
        url: action_url,
        autoProcessQueue : true,
        parallelUploads: 10,
        maxFiles: max_files,
        addRemoveLinks: true,
        dictResponseError: 'Error uploading file!',
        acceptedFiles: file_types,
        headers: {
            'X-CSRFToken': csrf_token
        },

        removedfile: function(file) {
            var _ref;
            $("input[data-org-name='"+ file.name + "']").eq(0).remove();
            return (_ref = file.previewElement) != null ? _ref.parentNode.removeChild(file.previewElement) : void 0;
        },

        init : function() {

            this.on("error", function (file, errorMessage, xhr) {
                alert(errorMessage);
            });

            this.on("success", function (file, rep) {

                var real_form = $("#" + real_frm_id);

                if (rep.status != 'success') {
                    JLib.small_box('File Upload Failed', rep.err_msg, false);
                    return;
                }

                /**
                 * generate form
                 */
                var hidden = $("<input>", {
                    'type': 'hidden',
                    'name': hidden_field_name,
                    'value': rep.file_name,
                    'data-org-name': rep.org_name
                }).appendTo(real_form);

            });
        } // /init

	});
};

/**
 * submit modal and fill up select2
 *
 * @param modal_id
 * @param url_to_option
 */
JLib.init_modal_select2 = function(modal_id, url_to_option) {

    url_to_option = url_to_option || '';

    if (modal_id == '' || typeof modal_id == 'undefined') {
        return;
    }

    $(modal_id).on('shown.bs.modal', function (event) {
        var modal = $(this);
        /* on trigger page */
        var trigger_button = $(event.relatedTarget); // Button that triggered the modal
        var select2 = trigger_button.closest('.input-group').find('select').eq(0);

        /* on modal page */
        var submit_btn = $(this).find('button[type="submit"]').eq(0);
        var form = submit_btn.closest('form');
        var ok_msg = submit_btn.data('ok-msg');

        submit_btn.off('click.select2_modal');
        submit_btn.on('click.select2_modal', function(e) {

            var action_url = form.attr('action');
            var data = form.serialize();

            $.ajax({
                url: action_url,
                dataType: 'json',
                type: 'post',
                data: data,
                success: function(rep) {
                    if(rep.status == 'error') {
                        JLib.small_box('Failed!', rep.message, false);
                        return;
                    }
                    /**
                     * if successfully,
                     * show message box and redirect to index page
                     */
                    JLib.small_box('Success', ok_msg, true);

                    /* add new option */
                    var option_url = '';
                    if (url_to_option != '') {
                        option_url = url_to_option + '?business_id=' + rep.id;
                    }
                    var o = $("<option/>", {value: rep.id, text: rep.text, 'data-url': option_url});
                    select2.append(o);

                    /* set value */
                    if (select2.prop('multiple')) {
                        var selected_val = select2.select2('val');
                        selected_val.push(rep.id);
                        select2.select2('val', selected_val)
                    } else {
                        select2.select2('val', rep.id);
                    }

                    select2.trigger('change');
                    modal.modal('hide');

                },
                complete: function (result) {
                    // modal.modal('hide');
                },
                error: function (data) {
                    alert('Cannot connect to server');
                    modal.modal('hide');
                }
            });

            e.preventDefault();
        });

    });
};

/**
 * ajax load bootstrap tab
 * 
 * @param container_id - tab header container, '#tab-header'
 */
JLib.init_ajax_tab = function(container_id){

    $(container_id).find('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
        var current_tab = $(e.target);
        var target_tab_id = current_tab.attr('href');
        var action_url = $(this).attr('data-url');
        if (action_url !== '' && typeof action_url != 'undefined') {
            $(target_tab_id).load(action_url, function(){
                $('.my-spin-placeholder').remove();
            });
        }
    });

    // register form click event
    var tabs = $(container_id).find('li > a[data-toggle="tab"]');
    $.each(tabs, function(){
        var tab = $(this);
        var target_tab_id = tab.attr('href');
        var action_url = tab.attr('data-url');
        if (action_url === '' || typeof action_url == 'undefined') {
            return true;
        }
        action_url = action_url.split('?')[0];
        $(target_tab_id).on('click', 'button[type="submit"]', function(e) {
            e.preventDefault();
            var form_param = $(this).closest('form').serializeForm();
            var new_url = action_url + '?' + $.param(form_param);

            tab.attr('data-url', new_url).trigger('show.bs.tab');
        });
    });

    $(container_id).find('li.active > a[data-toggle="tab"]').trigger('show.bs.tab');
};

/**
 * ajax load div
 * 
 * @param container - div id
 */
JLib.init_ajax_div = function(container, param_dict){

    param_dict = param_dict || {};
    var action_url = container.attr('data-url') + '?' + $.param(param_dict);
    
    $.ajax({
        url: action_url,
        dataType: 'html',
        success: function(html) {
            container.html(html);
        }
    });
    
};

/**
 * init switch checkbox. if clicked, send ajax post to server
 *
 * @param selector  - checkbox selector
 * @param msg_title - message title shown on screen whatever success or fail
 * @param j_table   - jquery table if checkbox is in a table
 * @param dt_table  - dataTable instance to refresh table
 */
JLib.init_switch_checkbox = function(selector, msg_title, j_table, dt_table) {

    var container = j_table || $('body');
    var token = container.data('token');

    container.delegate(selector, "click", function(e) {

        var checkbox = $(this);
        var action_url = checkbox.attr('data-url');
        if (action_url == '') {
            return;
        }

        $.ajax({
            url : action_url,
            type : 'post',
            dataType : 'json',
            headers: {
                'X-CSRFToken': token
            },
            data : {},
            beforeSend: function() {
                checkbox.prop('disabled', true);
            },
            success : function(rep) {
                if(rep.status == 'error') {
                    JLib.small_box(msg_title + ' Failed!', rep.message, false);
                    return;
                }
                /**
                 * if successfully,
                 * show message box and refresh table
                 */
                JLib.small_box(msg_title + ' Successfully!', rep.message, true);

                if (typeof dt_table != 'undefined') {
                    // dt_table.fnClearTable();
                }

            }, // /success
            complete: function() {
                checkbox.prop('disabled', false);
            }
        }); // /ajax

	});
};

JLib.init_print_btn = function(btn_selector, area_selector) {

    btn_selector.on('click', function() {
        area_selector.print({
            noPrintSelector: ".hidden-print",
            timeout: 2000
        });
    });
};

/**
 * submit a dynamic form
 *
 * @param url   - form url
 * @param args  - fields
 * @param name  -
 */
JLib.open_post_window = function(url, args, name){

    /*
     * generate form
     */
    var form = $("<form></form>",{

        'id':'tempForm',
        'method':'post',
        'action':url,
        'target':name,
        'style':'display:none'

    }).appendTo($("body"));

    /*
     * generate fields
     */
    for(var i in args){
        form.append($("<input>",{'type':'hidden','name':i,'value':args[i]}));
    }

    /*
     * bind submit event
     */
    form.bind('submit',function(){
        window.open("about:blank",name);
    });

    /*
     * submit form
     */
    form.trigger("submit");

    /*
     * remove form
     */
    form.remove();

};


JLib.repayment_p_and_i = function(principal, rate, period) {
    /**
     * M = P * i * (1 + i)^m / (1 + i)^m - 1
     *
     * P: principal
     * i: rate / 12
     * m: period(years) * 12
     * M: monthly repayment
     */
    var i = rate / 100 / 12;
    var m = period * 12;

    if (i ==0 || period == 0) {
        return 0;
    }

    var M = principal * i * Math.pow((1 + i), m) / (Math.pow((1 + i), m) - 1);

    return M.toFixed(2);
};


JLib.repayment_i = function(principal, rate, period) {
    /**
     * M = P * R * Period(year) / 12
     *
     * P: principal
     * R: rate
     * M: monthly repayment
     */
    if (rate == 0 || period == 0) {
        return 0;
    }
    var M = principal * (rate / 100) * period / (period * 12);

    return M.toFixed(2);
};


JLib.stamp_duty_nsw = function(property_price) {
    /**
     * M = P * R * Period(year) / 12
     *
     * P: principal
     * R: rate
     * M: monthly repayment
     */
    if (property_price == 0) {
        return 0;
    }

    var M = principal * (rate / 100) * period / (period * 12);

    return M.toFixed(2);
};


JLib.number_format = function(number, decimals, dec_point, thousands_sep) {
    // example 1: number_format(1234.56);
    // returns 1: '1,235'
    // example 2: number_format(1234.56, 2, ',', ' ');
    // returns 2: '1 234,56'
    // example 3: number_format(1234.5678, 2, '.', '');
    // returns 3: '1234.57'
    // example 4: number_format(67, 2, ',', '.');
    // returns 4: '67,00'
    // example 5: number_format(1000);
    // returns 5: '1,000'
    // example 6: number_format(67.311, 2);
    // returns 6: '67.31'
    // example 7: number_format(1000.55, 1);
    // returns 7: '1,000.6'
    // example 8: number_format(67000, 5, ',', '.');
    // returns 8: '67.000,00000'
    // example 9: number_format(0.9, 0);
    // returns 9: '1'
    // example 10: number_format('1.20', 2);
    // returns 10: '1.20'
    // example 11: number_format('1.20', 4);
    // returns 11: '1.2000'
    // example 12: number_format('1.2000', 3);
    // returns 12: '1.200'
    // example 13: number_format('1 000,50', 2, '.', ' ');
    // returns 13: '100 050.00'
    // example 14: number_format(1e-8, 8, '.', '');
    // returns 14: '0.00000001'

    number = (number + '').replace(/[^0-9+\-Ee.]/g, '');
    var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function (n, prec) {
    var k = Math.pow(10, prec);
    return '' + (Math.round(n * k) / k)
    .toFixed(prec);
    };
    // Fix for IE parseFloat(0.55).toFixed(0) = 0;
    s = (prec ? toFixedFix(n, prec) : '' + Math.round(n))
    .split('.');
    if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '')
    .length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1)
    .join('0');
    }
    return s.join(dec);
};


JLib.keep_tab_status = function(head_id, para_name) {
    
    if (typeof(Storage) == "undefined") {
        return;
    }


    $('a[data-toggle="tab"]').on('show.bs.tab', function(e) {
        try {
            sessionStorage.setItem(para_name, $(e.target).attr('href'));
        } catch (e) {
            // safari
            return ;
        }
    });

    var active_tab = sessionStorage.getItem(para_name);
    if(active_tab){
        $('#'+head_id+' a[href="' + active_tab + '"]').tab('show');

    }
};


JLib.double_confirm_submit = function (btn_obj, form_obj, title, msg_or_callback) {

	btn_obj.click(function(e){

        var msg = '';
        if (typeof msg_or_callback == 'function') {
            msg = msg_or_callback();

        } else if (typeof msg_or_callback == 'string') {
            msg = msg_or_callback;
        }

        $.SmartMessageBox({
            title : title,
            content : 'Are you sure to submit this form? ' + msg,
            buttons : '[No][Yes]'
        }, function(ButtonPressed) {

            if (ButtonPressed === "Yes") {
                form_obj.submit();
            }
        });

        e.preventDefault();
	});
};

JLib.truncate_char = function(s, char_cnt) {
    if (s.length <= char_cnt) {
        return s;
    }
    return $.trim(s).substring(0, char_cnt) + " ...";
};