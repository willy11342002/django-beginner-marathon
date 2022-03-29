from django.contrib.admin.templatetags.base import InclusionAdminNode
from django.contrib.admin.views.main import SEARCH_VAR
from django.template import Library

register = Library()
def advance_search_form(cl):
    """
    Display a search form for searching the list.
    """
    return {
        'cl': cl,
        'show_result_count': cl.result_count != cl.full_result_count,
        'search_var': SEARCH_VAR
    }
@register.tag(name='advance_search_form')
def search_form_tag(parser, token):
    return InclusionAdminNode(parser, token, func=advance_search_form, template_name='advance_search_form.html', takes_context=False)
