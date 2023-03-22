/**
 * This file is for generating DataTable*
 */
var JLib = window.JLib || {};

/**
 * initial JQuery Datatables v1.9 and earlier
 *  ref. http://legacy.datatables.net/examples/
 *
 *  usage:
 *      var dt_table = JLib.init_data_table('#new-property-table', true, false, '', 5, true, 'search-form');
 *
 *  table_selector - JQuery table selector, such as '#id' or '.class_name'
 *  has_page  - true/false. whether need pagination
 *  has_search - true/false.
 *  search_input_id
 *  order_by - column index, default order by
 *  auto_width
 *  param_form_id - form id if you want to send extra form parameters to server when soring or paginating
 *  {*|jQuery}
 */
JLib.init_data_table = function(table_selector, has_page, search_input_id, order_by,
                                auto_width, param_form_id, show_length_change, server_callback) {
    "use strict";
    order_by = order_by || 0;
    auto_width = auto_width || true;
    show_length_change = show_length_change || false;
    search_input_id = search_input_id || '';
    var has_search = search_input_id != '';
    server_callback = server_callback || '';

    var length_menu = [];
    var sdom = "'frti<\"text-center\"p>'";
    if (show_length_change) {
        length_menu = [[10, 30, 100, 9999], [10, 30, 100, 9999]];
        sdom = "<'dt-toolbar'r>t<'row mt20'<'col-xs-12 col-sm-6'<'custom-footer'>><'col-xs-12 col-sm-6'pl>>";
    }

    var server_side = true;
    var server_url = $(table_selector).attr('data-server-url');
    /*
     * For some browsers, `attr` is undefined; for others,
     * `attr` is false.  Check for both.
     */
    if (typeof server_url === typeof undefined || server_url === false) {
        server_side = false;
        server_url = '';
    }

   /*
    * init datatables
    */
    var ot_table = $(table_selector).dataTable({

        "bFilter" : has_search,             // no searching
        "bPaginate" : has_page,             // no paginating
        "bLengthChange" : show_length_change,   // no entries selection
        "aLengthMenu": length_menu,
        "bInfo" : false,                    // no foot information
        "bAutoWidth": false,
        "deferRender": true,
        "iDisplayLength" : 20,              // number of rows for per page
        "sPaginationType" : "full_numbers", // pagination type - full number, such as 1,2, ...
        "sDom" : sdom,                      // pagination layout - center
        "aaSorting" : [[order_by, 'desc']],        // by default, sorting by first column

        "aoColumnDefs": [
            { 'bSortable': false, 'aTargets': [ 'unsorted' ] },       // unsorted columns - class = 'unsorted'
            { 'bSearchable': false, 'aTargets': [ 'unsearchable' ] }    // unsearchable columns - class = 'unsearchable'
        ],

        "bProcessing": false,
        "bServerSide": server_side,
        "sAjaxSource": server_url,
        "sServerMethod": "GET",
        "fnServerParams": function (aoData) {

            if (typeof param_form_id !== typeof undefined && param_form_id != '') {
                var form_param = $('#' + param_form_id).serializeForm();
                for (var i in form_param) {
                    if (!form_param.hasOwnProperty(i)) {
                        continue;
                    }
                    // alert('name:' + i+ '; value: ' + server_params[i]);
                    aoData.push( { "name": i, "value": form_param[i] } );
                }
            }
        },
        "fnServerData": function ( sSource, aoData, fnCallback ) {
			/* Add some extra data to the sender */
			// aoData.push( { "name": "more_data", "value": "my_value" } );
			$.getJSON( sSource, aoData, function (json) {
				/* Do whatever additional processing you want on the callback, then tell DataTables */
                // console.log(json);
                
                /* callback */
                if (typeof server_callback == 'function') {
                    server_callback(json);
                }
                
				fnCallback(json);
			} );
		},
        /*
        "fnRowCallback": function( nRow, aData, iDisplayIndex ) {
            $(nRow).addClass('gradeA');
            return nRow;
        },*/
        "fnDrawCallback": function( oSettings ) {
            $('[rel="tooltip"]').tooltip();
        },
        /* display language */
        "oLanguage" : {
            "sEmptyTable" : '<div class="text-center">-- No record --</div>',
            "sZeroRecords" : '<div class="text-center">-- No record --</div>',
            "oPaginate": {
            "sFirst" : "<<",
            "sPrevious" : "<",
            "sNext" : ">",
            "sLast" : ">>"
            }
        }
    });

    /*
     * with search function
     * delay search for performance
     */
    var delay_timer = null;
    if (has_search) {
        /* hide default search-input field */
        $(".dataTables_filter").hide();
        /* bind search input field by id */
        var search_obj = $('#' + search_input_id);
        search_obj.bind('keyup', function(e) {
            if (delay_timer) {
                window.clearTimeout(delay_timer);
            }
            delay_timer = window.setTimeout(function() {
                $(table_selector).dataTable().fnFilter(search_obj.val());
            }, 200);
        });
    }

    return ot_table;

}; // function


JLib.init_column_picker = function (dt_table, table_id) {

    var column_arr = dt_table.fnSettings().aoColumns;
    var column_cnt = column_arr.length;
    var column_list_container = $('.columns-filter');

    var hidden_column_cnt = 0;
    for (var idx = 0; idx < column_cnt; idx++) {

        var column_obj = column_arr[idx];
        var column_title = column_obj.sTitle;
        var column_jquery_obj = $(table_id).find('th').eq(idx - hidden_column_cnt);

        // alert("idx: " + idx + "; title: " + column_jquery_obj.text());
        if (column_jquery_obj.hasClass("unpickable")) {
            continue;
        }

        var checked = true;
        if (column_jquery_obj.hasClass("default-hidden")) {
            checked = false;
            dt_table.fnSetColumnVis(idx, false);
            hidden_column_cnt++;
        }

        var checkbox = $("<input>", {"type": "checkbox", "value": idx}).prop("checked", checked);
        var label = $("<label></label>").append(checkbox).append(" "+column_title);
        $("<li></li>").append(label).appendTo(column_list_container);

        checkbox.on('click', {arg1: idx}, function(e){
            var column_idx = e.data.arg1;
            var column_obj = dt_table.fnSettings().aoColumns[column_idx];
            var column_visible = column_obj.bVisible;

            // alert("idx: "+ column_idx + " visible: " + column_visible);
            dt_table.fnSetColumnVis(column_idx, column_visible ? false : true );

            e.stopPropagation();
        });

        label.on('click', function(e){
            e.stopPropagation();
        });
    }
};

JLib.customized_report_download = function (btn_selector, column_filter_selector,
                                             search_input_selector, status_selector) {

    $(btn_selector).click(function(e) {
        e.preventDefault();

        var search = $(search_input_selector).val();
        var status = $(status_selector).find("option:selected").attr("data-status");
        if (typeof status == typeof undefined) {
            status = '';
        }

        var download_url = $(this).attr("href");
        if (download_url == '') {
            return;
        }

        var column_id_arr = [];
        $(column_filter_selector).find("input[type='checkbox']:checked").each(function(){
            var column_id = $(this).val();
            column_id_arr.push(column_id);
        });

        if (column_id_arr.length == 0) {
            alert('No column selected');
            return;
        }

        var delimiter = '?';
        if (download_url.indexOf("?") >= 0) {
             delimiter = '&'
        }
        download_url += delimiter + 'status=' + status + '&search=' + search + '&col_ids=' + column_id_arr.join(", ");
        window.location.href = download_url;
    });
};


