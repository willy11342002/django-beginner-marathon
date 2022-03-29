from django.contrib.admin.utils import lookup_needs_distinct
from django.contrib.admin.views.main import ERROR_FLAG
from django.utils.translation import gettext_lazy as _
from django.utils.text import unescape_string_literal
from django.utils.text import smart_split
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.db import models
from functools import reduce
import operator
import copy


class ModelAdmin(admin.ModelAdmin):
    change_list_template = 'admin/advance_change_list.html'
    class Media:
        css = {
            'all': ('css/web/admin.css',)
        }

    other_search_fields = {}
    search_fields = (
        # (_('translate fieldname'), 'fieldname'),
    )

    def changelist_view(self, request, extra_context=None, **kwargs):
        request.GET._mutable = True

        search_fields = [field for fieldname, field in self.search_fields] + ['e', 'joiner', 'regex', 'all']
        for field, rule in request.GET.items():
            if field not in search_fields:
                return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')
        self.other_search_fields = {
            field: request.GET.pop(field, [''])
            for fieldname, field in self.search_fields
        }
        self.search_joiner = request.GET.pop('joiner', ['and_'])[0]
        if self.search_joiner not in ['and_', 'or_']:
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')
        self.search_regex = request.GET.pop('regex', [''])[0]
        if self.search_regex not in ['1', '']:
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        request.GET_mutable = False
        return super().changelist_view(request, extra_context=extra_context)

    def get_search_results(self, request, queryset, search_term):
        may_have_duplicates = False
        orm_lookups = []
        or_queries = []
        for search_field, search_term in self.other_search_fields.items():
            if search_term == ['']:
                continue
            if self.search_regex:
                lookup = f'{search_field}__iregex'
            else:
                lookup = search_field

            orm_lookups.append(lookup)
            for bit in smart_split(search_term[0]):
                if bit.startswith(('"', "'")) and bit[0] == bit[-1]:
                    bit = unescape_string_literal(bit)
                or_queries.append(models.Q(**{lookup: bit}))

        if or_queries:
            joiner = getattr(operator, self.search_joiner)
            queryset = queryset.filter(reduce(joiner, or_queries))

        may_have_duplicates |= any(
            lookup_needs_distinct(self.opts, search_spec)
            for search_spec in orm_lookups
        )
        return queryset, may_have_duplicates


    def get_template_search_fields(self, request):
        result = copy.deepcopy(super().get_search_fields(request))
        result = {r[1]: list(r) for r in result}
        for k, v in self.other_search_fields.items():
            result[k] += [v[0]]
        result = tuple(result.values())
        return result

    def get_changelist_instance(self, request):
        """
        Return a `ChangeList` instance based on `request`. May raise
        `IncorrectLookupParameters`.
        """
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        # Add the action checkboxes if any actions are available.
        if self.get_actions(request):
            list_display = ['action_checkbox', *list_display]
        sortable_by = self.get_sortable_by(request)
        ChangeList = self.get_changelist(request)
        changelist = ChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            self.get_list_filter(request),
            self.date_hierarchy,
            self.get_template_search_fields(request),
            self.get_list_select_related(request),
            self.list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
            sortable_by,
        )
        changelist.joiner = self.search_joiner
        changelist.regex = self.search_regex
        fields_dic = {
            **{
                f.name: [[str(c[0]), str(c[1])] for c in f.choices]
                for f in self.model._meta.fields
                if f.choices
            },
            **{
                f.name: [['True', '是'], ['False', '否']]
                for f in self.model._meta.fields
                if type(f) == models.BooleanField
            }
        }
        changelist.chooser = {
            field: fields_dic.get(field)
            for fieldname, field in self.search_fields
            if fields_dic.get(field)
        }
        return changelist
