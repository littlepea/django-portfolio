# -*- coding: utf-8 -*-

from django import template
from portfolio import models

register = template.Library()


@register.assignment_tag()
def artworks(collection=None, category=None, offset=0, limit=10000):
    """
    Returns a list of artworks optionally filtered by category/collection (with offset/limit)

    :param context: RequestContext
    :param collection: (optional) Collection object, id or slug to filter artworks by collection
    :param category: (optional) Category object, id or slug to filter artworks by category
    :param offset: (optional) Offset for objects list (default: 0)
    :param limit: (optional) Limit for objects list (default: 10000)
    :return: List of Artworks
    """
    filters = {}
    try:
        if category:
            if type(category) not in [models.Category, int]: # assume Category.slug
                category = models.Category.objects.get(slug=category)
            filters['categories'] = category
        if collection:
            if type(collection) not in [models.Collection, int]: # assume Collection.slug
                collection = models.Collection.objects.get(slug=collection)
            filters['collection'] = collection
        object_list = models.Artwork.objects.filter(**filters)[offset:offset+limit]
    except:
        object_list = []
    return object_list


@register.assignment_tag()
def categories(offset=0, limit=10000):
    """
    Returns a list of categories (with offset/limit).

    :param context: RequestContext
    :param offset: (optional) Offset for objects list (default: 0)
    :param limit: (optional) Limit for objects list (default: 10000)
    :return: List of Categories
    """
    return models.Category.objects.all()[offset:offset+limit]


@register.assignment_tag()
def collections(offset=0, limit=10000):
    """
    Returns a list of collections (with offset/limit).

    :param context: RequestContext
    :param offset: (optional) Offset for objects list (default: 0)
    :param limit: (optional) Limit for objects list (default: 10000)
    :return: List of Collections
    """
    return models.Collection.objects.all()[offset:offset+limit]