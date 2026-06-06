from django import template

register = template.Library()

@register.simple_tag
def filter_day_attendance(attendance_map, day):
    """Retrieves attendance record for a specific day from mapping dictionary."""
    return attendance_map.get(day)
