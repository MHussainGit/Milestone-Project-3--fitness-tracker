"""
Template tags for accessible form rendering.
"""
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def add_class(value, arg):
    """
    Add a CSS class to an HTML element.
    Usage: {{ field|add_class:"form-control" }}
    """
    return value.as_widget(attrs={"class": arg})


@register.filter
def add_aria_describedby(field, ids):
    """
    Add aria-describedby attribute to form field.
    Usage: {{ field|add_aria_describedby:"error-field help-field" }}
    """
    if not ids:
        return field
    
    attrs = field.field.widget.attrs.copy()
    attrs['aria-describedby'] = ids
    field.field.widget.attrs = attrs
    return field


@register.simple_tag
def form_field_with_errors(field):
    """
    Render a form field with proper accessibility attributes for errors.
    """
    error_id = f"error-{field.id_for_label}" if field.errors else None
    help_id = f"help-{field.id_for_label}" if field.help_text else None
    
    described_by = []
    if error_id:
        described_by.append(error_id)
    if help_id:
        described_by.append(help_id)
    
    aria_describedby = " ".join(described_by) if described_by else None
    
    return {
        'field': field,
        'error_id': error_id,
        'help_id': help_id,
        'aria_describedby': aria_describedby,
    }
