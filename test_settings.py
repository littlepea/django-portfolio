DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'portfolio.context_processors.collections',
    'portfolio.context_processors.artworks',
    'portfolio.context_processors.categories'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'sorl.thumbnail',
    'portfolio'
)

ROOT_URLCONF = 'test_urls'

SITE_ID = 1
