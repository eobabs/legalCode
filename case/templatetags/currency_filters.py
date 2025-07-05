from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def naira(value):
    try:
        formatted_value = "{:,.2f}".format(float(value))
        return mark_safe(f"₦{formatted_value}")
    except (ValueError, TypeError):
        return "₦0.00"

@register.filter
def naira_no_decimal(value):
    try:
        float_value = float(value)
        if float_value.is_integer():
            formatted_value = "{:,.0f}".format(float_value)
        else:
            formatted_value = "{:,.2f}".format(float_value)
        return mark_safe(f"₦{formatted_value}")
    except (ValueError, TypeError):
        return "₦0"