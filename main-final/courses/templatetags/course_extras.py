from django import template
from urllib.parse import urlencode
from django.utils import timezone
from datetime import datetime
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
@register.filter
def get_item(dictionary, key):
    """Safely get a value from a dictionary with a string key"""
    if hasattr(dictionary, 'get'):
        return dictionary.get(str(key), 0)  # Returns 0 if key doesn't exist
    return 0  # Return 0 if input isn't a dictionary

@register.filter
def rating_count(course, rating):
    """Returns count of reviews with specific rating for a course"""
    return course.reviews.filter(rating=rating).count()


@register.filter
def relative_time(value):
    now = timezone.now()
    diff = now - value

    seconds = diff.total_seconds()
    days = diff.days

    if days > 365:
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif days > 30:
        months = days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif days > 0:
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds > 3600:
        hours = seconds // 3600
        return f"{int(hours)} hour{'s' if hours != 1 else ''} ago"
    elif seconds > 60:
        minutes = seconds // 60
        return f"{int(minutes)} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"