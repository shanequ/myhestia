from __future__ import unicode_literals
import copy
import os
import uuid
from django.http import HttpResponse
import xlwt
from myhestia.settings import TMP_FILE_ROOT


class Arial10(object):
    _char_widths = {
        '0': 262.637,
        '1': 262.637,
        '2': 262.637,
        '3': 262.637,
        '4': 262.637,
        '5': 262.637,
        '6': 262.637,
        '7': 262.637,
        '8': 262.637,
        '9': 262.637,
        'a': 262.637,
        'b': 262.637,
        'c': 262.637,
        'd': 262.637,
        'e': 262.637,
        'f': 146.015,
        'g': 262.637,
        'h': 262.637,
        'i': 117.096,
        'j': 88.178,
        'k': 233.244,
        'l': 88.178,
        'm': 379.259,
        'n': 262.637,
        'o': 262.637,
        'p': 262.637,
        'q': 262.637,
        'r': 175.407,
        's': 233.244,
        't': 117.096,
        'u': 262.637,
        'v': 203.852,
        'w': 321.422,
        'x': 203.852,
        'y': 262.637,
        'z': 233.244,
        'A': 321.422,
        'B': 321.422,
        'C': 350.341,
        'D': 350.341,
        'E': 321.422,
        'F': 291.556,
        'G': 350.341,
        'H': 321.422,
        'I': 146.015,
        'J': 262.637,
        'K': 321.422,
        'L': 262.637,
        'M': 379.259,
        'N': 321.422,
        'O': 350.341,
        'P': 321.422,
        'Q': 350.341,
        'R': 321.422,
        'S': 321.422,
        'T': 262.637,
        'U': 321.422,
        'V': 321.422,
        'W': 496.356,
        'X': 321.422,
        'Y': 321.422,
        'Z': 262.637,
        ' ': 146.015,
        '!': 146.015,
        '"': 175.407,
        '#': 262.637,
        '$': 262.637,
        '%': 438.044,
        '&': 321.422,
        '\'': 88.178,
        '(': 175.407,
        ')': 175.407,
        '*': 203.852,
        '+': 291.556,
        ',': 146.015,
        '-': 175.407,
        '.': 146.015,
        '/': 146.015,
        ':': 146.015,
        ';': 146.015,
        '<': 291.556,
        '=': 291.556,
        '>': 291.556,
        '?': 262.637,
        '@': 496.356,
        '[': 146.015,
        '\\': 146.015,
        ']': 146.015,
        '^': 203.852,
        '_': 262.637,
        '`': 175.407,
        '{': 175.407,
        '|': 146.015,
        '}': 175.407,
        '~': 291.556}

    # By default, Excel displays column widths in units equal to the width
    # of '0' (the zero character) in the standard font.  For me, this is
    # Arial 10, but it can be changed by the user.  The BIFF file format
    # stores widths in units 1/256th that size.
    #
    # Within Excel, the smallest incrementable amount for column width
    # is the pixel.  However many pixels it takes to draw '0' is how many
    # increments there are between a width of 1 and a width of 2.  A
    # request for a finer increment will be rounded to the nearest pixel.
    # For Arial 10, this is 9 pixels, but different fonts will of course
    # require different numbers of pixels, and thus have different column
    # width granularity.
    #
    # So far so good, but there is a wrinkle.  Excel pads the first unit
    # of column width by 7 pixels.  At least this is the padding when the
    # standard font is Arial 10 or Courier New 10, the two fonts I've tried.
    # It don't know if it's different for different fonts.  For Arial 10,
    # with a padding of 7 pixels and a 9-pixel-wide '0', this results in 16
    # increments to get from width 0 (hidden) to width 1.  Ten columns of
    # width 1 are 160 pixels wide while five columns of width 2 are 125
    # pixels wide.  A single column of width 10 is only 97 pixels wide.
    #
    # The punch line is that pixels are the true measure of width, and
    # what Excel reports as the column width is wonky between 0 and 1.
    # The only way I know to find out the padding for a desired font is
    # to set that font as the standard font in Excel and count pixels.

    @classmethod
    def colwidth(cls, n):
        """ Translate human-readable units to BIFF column width units"""
        if n <= 0:
            return 0
        if n <= 1:
            return n * 456
        return 200 + n * 256

    @classmethod
    def fit_width(cls, data):
        """Try to auto fit Arial 10"""
        _max_units = 0
        if not isinstance(data, str) and not isinstance(data, unicode):
            data = str(data)

        for _data in data.split("\n"):
            units = 400
            for _char in _data:
                if _char in cls._char_widths:
                    units += cls._char_widths[_char]
                else:
                    units += cls._char_widths['0']
            if _max_units < units:
                _max_units = units

        _max_units *= 1.1
        return int(max(_max_units, 700))  # Don't go smaller than a reported width of 2


class SimpleXLS:

    ALIGNMENT = xlwt.Alignment
    HEADER_HEIGHT = 450
    ROW_HEIGHT = 400
    COLUMN_MIN_WIDTH = 8    # chars

    FORMAT_MONEY = '#,##0.00'
    FORMAT_INT = '#,##0'

    def __init__(self, sheet_name='sheet'):

        self.xls_file = xlwt.Workbook(encoding='utf8', style_compression=2)
        self.sheet = self.xls_file.add_sheet(sheet_name)

        #
        # header column list
        #
        self.header_list = []

        #
        # header style
        #
        _header_font = xlwt.Font()
        _header_font.bold = True
        _header_font.colour_index = xlwt.Style.colour_map['white']

        xlwt.add_palette_colour("header_colour", 0x21)
        self.xls_file.set_colour_RGB(0x21, 61, 133, 198)

        _header_pattern = xlwt.Pattern()
        _header_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        _header_pattern.pattern_fore_colour = 0x21

        self.header_style = xlwt.XFStyle()
        self.header_style.font = _header_font
        self.header_style.pattern = _header_pattern

        #
        # data style
        #
        xlwt.add_palette_colour("data_strip_colour", 0x22)
        self.xls_file.set_colour_RGB(0x22, 207, 226, 243)

        self.data_style = xlwt.XFStyle()

        # column width dict
        self.column_width_dict = {}

    def _write_xls_row(self, row, data_list, style, row_height, fill_stripped=False):
        """
            Write a single xls row to file
        """
        _style = copy.deepcopy(style)
        if fill_stripped:
            _pattern = xlwt.Pattern()
            _pattern.pattern = xlwt.Pattern.SOLID_PATTERN
            _pattern.pattern_fore_colour = 0x22
            _style.pattern = _pattern

        for idx, column_data in enumerate(data_list):
            _data = column_data.get('data', '')
            _align = column_data.get('align', self.ALIGNMENT.HORZ_LEFT)
            _format = column_data.get('format', 'general')
            _min_width = column_data.get('min_width', self.COLUMN_MIN_WIDTH)
            _merge = column_data.get('merge', [])

            alignment = xlwt.Alignment()
            alignment.horz = _align
            alignment.vert = self.ALIGNMENT.VERT_CENTER
            _style.alignment = alignment

            self.sheet.row(row).height_mismatch = True
            self.sheet.row(row).height = row_height

            _style.num_format_str = _format

            if _merge:
                self.sheet.write_merge(_merge[0], _merge[1], _merge[2], _merge[3], _data, _style)
            else:
                self.sheet.write(row, idx, _data, _style)

            try:
                _width = Arial10.fit_width(str(_data))
            except UnicodeEncodeError:
                _width = _min_width

            _min_width = Arial10.colwidth(_min_width)
            if _width < _min_width:
                _width = _min_width
            if _width > self.column_width_dict.get(idx, 0) and not _merge:
                self.column_width_dict[idx] = _width
                self.sheet.col(idx).width = _width

    def set_header(self, header_list):
        self.header_list = header_list
        _header_names = [d['name'] for d in header_list]

        self._write_xls_row(0, _header_names, self.header_style, self.HEADER_HEIGHT)

    def write_header(self, row, data_list, style=None):
        _style = style if style else self.header_style
        self._write_xls_row(row, data_list, _style, self.HEADER_HEIGHT)

    def write_row(self, row, data_list, fill_stripped=False):
        return self._write_xls_row(row, data_list, self.data_style, self.ROW_HEIGHT, fill_stripped)

    def make_response(self, file_name=''):
        if not file_name:
            file_name = self.sheet.name

        response = HttpResponse(content_type='text/xls')
        response['Content-Disposition'] = 'attachment; filename="%s' % file_name

        self.xls_file.save(response)
        return response

    def save_to_tmp(self):
        """
            Throw IOError
        """
        _file_name = "%s.xls" % uuid.uuid4()
        _file_path = os.path.join(TMP_FILE_ROOT, _file_name)

        self.xls_file.save(_file_path)

        return _file_name
