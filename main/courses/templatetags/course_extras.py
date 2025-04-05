from django import template
from urllib.parse import urlencode
register = template.Library()

@register.filter
def subtract(value, arg):
    """Subtracts arg from value"""
    return value - arg

@register.filter
def get_range(value):
    """Returns range up to value"""
    return range(int(value))

@register.filter
def show_stars(value):
    full_stars = int(value)
    half_star = (value - full_stars) >= 0.3
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    stars = []
    stars.extend(['fas fa-star'] * full_stars)
    if half_star:
        stars.append('fas fa-star-half-alt')
    stars.extend(['far fa-star'] * empty_stars)
    
    return stars

@register.simple_tag
def preserve_filters(request, param_name, param_value):
    params = request.GET.copy()
    params[param_name] = param_value
    return params.urlencode()

@register.simple_tag
def modify_query(*args, **kwargs):
    request = kwargs.pop('request')
    query_dict = request.GET.copy()
    
    for key, value in kwargs.items():
        if value is None:
            if key in query_dict:
                del query_dict[key]
        else:
            query_dict[key] = value
    
    return query_dict.urlencode()