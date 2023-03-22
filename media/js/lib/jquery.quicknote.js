var QNLib = window.QNLib || {};

QNLib.isURL = function(str) {
	// CHECKING IF NOTE IS HAS URL FORMAT
	if(/(http|https|ftp):\/\/[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$/i.test(str)) {
		return true;
	} else {
		return false;
	}
};

QNLib._make_new_note = function (data, user_id) {

	var note_text = data.note;
	var note_id = 'qn_note_' + data.id;
	var created_by = data.created_by;
	var created_at = data.created_at;

	var row = $('<div class="row">').prependTo('#qn_notes_panel');
	var col = $('<div class="col-sm-12">').appendTo(row);
	var text = '<span class="qn_notes_text">'+ note_text +'</span>'+ '<br><span class="text-right pull-right"> -- ' + created_by + ' ' + created_at + '</span>';
	$('<span class="quicknote pull-right" id="' + note_id + '"></span>').css({ display: 'table' }).stop().fadeIn('fast').appendTo(col).html(text);

	if (user_id == data.created_by_id) {
		$('<span class="close" data-note-id="'+data.id+'"></span>').prependTo('#' + note_id);
	}

	//$('<span class="close"></span>').appendTo('#' + data.id);

	if (QNLib.isURL(data.note)) {
		$('#' + id).addClass('quicknote-bword');
	}
};

QNLib.fleshNote = function (j_obj, action_url, user_id) {

	// clean all notes
	$('#qn_notes').find('span').remove();

	// write new
	$.ajax({
		url: action_url ,
		dataType: 'json',
		success: function(rep) {
			if(rep.status != 'ok') {
				JLib.small_box('Fetch notes failed!', rep.message, false);
				return;
			}

			$.each(rep.data, function(index, note) {
				QNLib._make_new_note(note, user_id);
			});

		},
		error: function (data) {
			alert('Cannot connect to server');
		}
	});

}
;(function($, window, document, undefined) {

	'use strict';

	var g_el, $el, action_url, g_config, user_id, delete_url;

	var QuickNote = function(el, options) {
		g_el = el;
		$el = $(el);
		this.options = options;
		action_url = $el.attr('data-url');
		delete_url = $el.attr('data-delete-url');
		user_id = $el.attr('data-user-id');
	};

	QuickNote.prototype = {
		defaults: {
			theme: 'dark',
			pos: 'right',
			storage: true || false
		},
		init: function() {

			g_config = $.extend({}, this.defaults, this.options);

			// THEME
			if (g_config.theme == 'light') {
				$el.addClass('qn_container_light').addClass('qn_container');
			} else if (g_config.theme == 'dark') {
				$el.addClass('qn_container');
			} else {
				console.log('Error: Theme >> ' + this.config.theme + ' not found.');
				// SET DEFAULT
				$el.addClass('qn_container');
			}

			// init element
			var showHide = '<div id="qn_sh"><span>Show/Hide</span></div>';
			var divNotes = '<div id="qn_notes"></div>';
			var notesInp = '<p><input type="text" name="qn_input" id="qn_notes_input" class="mb5" maxlength="500" placeholder="Your notes..."><div id="qn_notes_panel"></p>';

			$(showHide).appendTo($el);
			$(divNotes).appendTo($el);
			$(notesInp).appendTo($el.find('#qn_notes'));


			// this.appendElem();
			QNLib.fleshNote($el, action_url, user_id);
			this.completeNote();

		},
		completeNote: function() {

			$el.on('keypress', '#qn_notes input', function(e) {
				// RETURN KEY PRESSED
				if (e.which == 13 || e.keyCode == 13) {

					var notesInpVal = $('#qn_notes input').val();
					if (notesInpVal == ''){
						JLib.small_box('Failed!', 'Empty notes', false);
						return;
					}

					if (!$('#qn_notes_panel').is(":visible")) {
						$('#qn_sh').find('span').trigger('click');
					}

					// clean input box
					$('.qn_container #qn_notes_input').val('');
					
					$.ajax({
						url: action_url,
						dataType: 'json',
						type: 'post',
						data: {notes: notesInpVal},
						success: function(rep) {
							if(rep.status != 'ok') {
								JLib.small_box('Failed!', rep.message, false);
								return;
							}

							var note = rep.data;
							QNLib._make_new_note(note, user_id);

						},
						complete: function (result) {

						},
						error: function (data) {
							alert('Cannot connect to server');
						}
					});
				}
			});

			// SHOW AND HIDE
			$el.on('click', '#qn_sh span', function() {
				$('#qn_notes_panel').slideToggle(100);
			});

			// CLICK TO CLOSE NOTES
			$el.on('click', '.quicknote .close', function() {
				var note_id = $(this).data('note-id');
				var remove_obj = $(this).closest('.row');
				$.ajax({
					url: delete_url,
					dataType: 'json',
					type: 'post',
					data: {sr_note_id: note_id},
					success: function(rep) {
						if(rep.status != 'ok') {
							JLib.small_box('Failed!', rep.message, false);
							return;
						}

						// REMOVE CURRENT ELEMENT FROM DOM
						remove_obj.stop().fadeOut(500, function() {
							$(this).remove();
						});
					},
					complete: function (result) {

					},
					error: function (data) {
						alert('Cannot connect to server');
					}
				});
				/*
				$(this).each(function() {
					$(this).parent('.quicknote').stop().fadeOut(100, function() {
						var id = $(this).attr('id');
						var note = $(this).text();
						var theNote = {
                            'id': id,
                            'note': note
                        };

						// REMOVAL OF ITEM IN localStorage
						if (storage === true) {
							var ls = JSON.parse(localStorage.getItem('quicknote')) || [];
							if (ls) {
								$.each(ls, function(index, obj) {
									// console.log(ID);
									if (obj.id == id) {
										ls.splice(index, 1);
										localStorage.setItem('quicknote', JSON.stringify(ls));
										return false;
									}
								});
							}
						}

						// REMOVE CURRENT ELEMENT FROM DOM
						$(this).parent('.quicknote').remove();
					});
				});
				*/
			});
		}
	};

	$.fn.quicknote = function(options) {
		return this.each(function() {
			new QuickNote(this, options).init();
		});
	};

})(jQuery, window, document);
