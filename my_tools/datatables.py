from __future__ import unicode_literals
import json

from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import View


class DataTableListView(View):
    """
        JQuery datatables server side processing ref.
            http://legacy.datatables.net/release-datatables/examples/server_side/server_side.html
    """
    model = None
    page_rows = 10
    table_columns = [
        'id',
    ]

    # request type for various display
    r_type = ''
    callback_data = {}

    def get(self, request):

        # request type
        self.r_type = request.GET.get('r_type', '')

        # calculate current page, display_length could not be 0
        display_length = int(request.GET.get('iDisplayLength', self.page_rows))
        current_page = int(request.GET.get('iDisplayStart', 0)) / display_length + 1

        echo = request.POST.get('sEcho', 0)

        # make 'order by'
        order_list = []
        sort_cols = int(request.GET.get('iSortingCols'))
        for i in range(sort_cols):
            sort_dir = "" if request.GET.get('sSortDir_%d' % i, '') == 'asc' else '-'
            col_name = self.table_columns[int(request.GET.get('iSortCol_%d' % i))]
            order_list.append("%s%s" % (sort_dir, col_name,))

        # make Django Paginator
        object_list = self.get_object_list(request, order_list)
        pages = Paginator(object_list, display_length)
        total = pages.count
        if current_page > pages.num_pages:
            current_page = pages.num_pages

        display_page = pages.page(current_page)

        # make result
        rows_list = []
        for i in display_page:
            rows_list.append(self.get_return_row(i, request))

        json_list = {
            'sEcho': echo,
            'iTotalRecords': total,
            'iTotalDisplayRecords': total,
            'aaData': rows_list,
            'callback_data': self.callback_data,
        }

        return HttpResponse(json.dumps(json_list, cls=DjangoJSONEncoder))

    def get_return_row(self, obj, request):
        return_list = []
        for i in self.table_columns:
            attr = getattr(obj, i)
            if hasattr(attr, '__call__'):
                return_list.append(str(attr()))
            else:
                return_list.append(str(attr))
        return return_list

    def get_filter(self, request):
        _ = self, request
        return Q()

    def get_exclude(self, request):
        _ = self, request
        return Q()

    def get_object_list(self, request, order_list):
        query_filter = self.get_filter(request)
        query_exclude = self.get_exclude(request)
        object_list = self.model.objects.filter(query_filter).exclude(query_exclude).order_by(*order_list)
        return object_list