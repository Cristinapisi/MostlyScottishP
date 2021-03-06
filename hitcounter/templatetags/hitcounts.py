from django import template
from hitcounter.models import Hit


register = template.Library()


@register.simple_tag(takes_context=True)
def pagehits(context):
    """
    pagehits for current page
    :param context:
    :return:
    """
    try:
        request = context['request']
        hits = Hit.objects.filter(url=request.path).count()
        return hits
    except Hit.DoesNotExist:
        return 0
    except KeyError:
        return 0


@register.simple_tag
def pagehits_url(url):
    """
    hits by url
    :param url:
    :return:
    """
    try:
        hits = Hit.objects.filter(url=url).count()
        return hits
    except Hit.DoesNotExist:
        return 0

