django-portfolio
================

.. image:: https://secure.travis-ci.org/dokterbob/django-portfolio.png
    :target: http://travis-ci.org/dokterbob/django-portfolio


What's this?
------------
An artist's portfolio as a pluggable Django app, based on the following
assumptions:

1. A portfolio consists of collections containing artworks.
2. Artworks have one or more pictures and (optionally) a title and a description.
3. Artworks can be listed from within collections or categories.

Features
--------
* Well tested, decent code coverage and used in production environments.
* Makes good use of Django's admin; drag and drop sorting, search, filtering, 
  pagination and thumbnail previews.
* All strings are fully translatable (will integrate with Transifex 
  on request, feel free to create a GitHub issue).
* Optional template context processors and sitemaps available.
* Very basic front-end templates to help kickstart integration.
* South migrations available for hassle-free upgrade paths.

Installation
------------
1. `pip install -e https://github.com/dokterbob/django-portfolio.git#egg=django-portfolio`
2. Follow `sorl-thumbnail's installation instructions <http://sorl-thumbnail.readthedocs.org/en/latest/installation.html#setup>`_.
3. Follow `django-admin-sortable's installation instructions <http://pypi.python.org/pypi/django-admin-sortable/>`_.
4. Add `portfolio` to `INSTALLED_APPS`.
5. Include URL's into Django's URL space, like such::

        urlpatterns = patterns('',
            (r'^portfolio/', include('portfolio.urls')),
            ...
        )

6. Have a cup of coffee! You deserve one; basic integration of the portfolio app is done now.

7. Copy the minimal base templates from the `templates folder <https://github.com/dokterbob/django-portfolio/tree/master/portfolio/templates>`_ to your project's template
   folder and start customizing.

8. (Optionally) Configure `sitemaps <https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/>`_ by updating
   your sitemaps dictionary with `portfolio.sitemaps.portfolio_sitemaps`.

   For example::

        from portfolio.sitemaps import portfolio_sitemaps

        sitemaps = {
            'blog': GenericSitemap(info_dict, priority=0.6),
        }

        sitemaps.update(portfolio_sitemaps)
        ...
        urlpatterns = patterns('',
            (r'^portfolio/', include('portfolio.urls')),

            # Sitemaps
            (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
                {'sitemaps': sitemaps}),
        )

9. (Optionally) Enable `template context processors <https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors>`_
   for `collections`, `artworks` and/or `categories`  in `settings.py`::

        TEMPLATE_CONTEXT_PROCESSORS = (
            ...
            'portfolio.context_processors.collections',
            'portfolio.context_processors.artworks'
            'portfolio.context_processors.categories'
        )



Template tags
--------

1. artworks
^^^^^^^^^^^

Returns a list of artworks optionally filtered by category/collection (with offset/limit).

Arguments:
* collection - (optional) Collection object, id or slug to filter artworks by collection
* category - (optional) Category object, id or slug to filter artworks by category
* offset - (optional) Offset for objects list (default: 0)
* limit - (optional) Limit for objects list (default: 10000)

Usage example::

    {% load portfolio_tags %}

    {% artworks collection="featured" as artwork_list %}

2. collections
^^^^^^^^^^^^^^

Returns a list of collections (with offset/limit).

Arguments:
* offset - (optional) Offset for objects list (default: 0)
* limit - (optional) Limit for objects list (default: 10000)

Usage example::

    {% load portfolio_tags %}

    {% collections as collection_list%}

3. categories
^^^^^^^^^^^^^

Returns a list of categories (with offset/limit).

Arguments:
* offset - (optional) Offset for objects list (default: 0)
* limit - (optional) Limit for objects list (default: 10000)

Usage example::

    {% load portfolio_tags %}

    {% categories as category_list %}
