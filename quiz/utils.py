DIFFICULTY_LEVELS = {
    "10": "Level 1 (Easy)",
    "50": "Level 2 (Medium)",
    "100": "Level 3 (Hard)",
}


from django import template

register = template.Library()


@register.filter
def get_difficulty_name(level):
    return DIFFICULTY_LEVELS.get(str(level), "Unknown")
