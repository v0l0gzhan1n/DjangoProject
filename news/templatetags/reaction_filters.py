from django import template

register = template.Library()

@register.filter(name='filter_reaction')
def filter_reaction(queryset, reaction_type):
    return [item for item in queryset if item['reaction_type'] == reaction_type]