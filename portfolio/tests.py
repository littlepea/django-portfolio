import imp

from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.conf import settings

from .models import Artwork, Category, Collection, Picture
from . import editor
from .templatetags import portfolio_tags


class PortfolioTestBase(TestCase):
    def _get_random_slug(self):
        """ Generate a random slug. """

        import uuid

        return str(uuid.uuid4().hex)[:30]

    def get_unique_slug(self, model, slug_field='slug'):
        """ Set slug to unique value. """

        slug = self._get_random_slug()
        while model.objects.filter(**{slug_field: slug}).exists():
            slug = self._get_random_slug()

        return slug

    def create_category(self, slug=None, title='Test category'):
        """ Create Category such that it can be saved, but don't save it. """

        if not slug:
            slug = self.get_unique_slug(Category)

        obj = Category(slug=slug, title=title)

        return obj

    def create_collection(self, slug=None, title='Test collection'):
        """ Create collection such that it can be saved, but don't save. """

        if not slug:
            slug = self.get_unique_slug(Category)

        obj = Collection(slug=slug, title=title)

        return obj

    def create_artwork(self, collection=None):
        """ Create artwork such that it can be saved - but don't save. """

        if not collection:
            collection = self.create_collection()
            collection.save()

        obj = Artwork(collection=collection)

        return obj

    def create_picture(self, artwork=None, title='Test picture'):
        """ Create Picture such that it can be saved, but don't. """

        if not artwork:
            artwork = self.create_artwork()
            artwork.save()

        obj = Picture(artwork=artwork, title=title)
        return obj


class HomeTests(PortfolioTestBase):
    """
    Test the home/root view: it should redirect to the collection list.
    """

    def test_redirect(self):
        """ Test whether the redirect works. """

        url = reverse('portfolio_home')
        collection_list_url = reverse('collection_list')

        # Attempt request
        response = self.client.get(url, follow=True)

        # Assure status is permanent redirect
        redirect = response.redirect_chain[0]
        self.assertIn(collection_list_url, redirect[0])
        self.assertEquals(redirect[1], 301)


class ArtworkTests(PortfolioTestBase):
    """ Tests for Artworks. """

    def test_create(self):
        """ Create and save Artwork. """

        obj = self.create_artwork()
        unicode(obj)
        obj.save()

    def test_listview(self):
        """ Test requesting the object. """

        obj = self.create_artwork()
        obj.save()

        url = reverse('artwork_list')
        self.assertTrue(url)

        # Attempt request
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # The title should be in the page, somewhere
        self.assertContains(response, obj.title)
        self.assertContains(response, obj.get_absolute_url())

    def test_detailview(self):
        """ Test requesting the object. """

        obj = self.create_artwork()
        obj.save()

        url = obj.get_absolute_url()
        self.assertTrue(url)

        # Make sure the slug is in there
        self.assertIn(str(obj.pk), url)

        # Attempt request
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # The title should be in the page, somewhere
        self.assertContains(response, obj.title)

    def test_categorydetailview(self):
        """ Make sure categories are listed in artwork detail. """

        category = self.create_category()
        category.save()

        obj = self.create_artwork()
        obj.save()

        obj.categories.add(category)

        url = obj.get_absolute_url()

        # Attempt request
        response = self.client.get(url)

        # The category title and URL should be in the page, somewhere
        self.assertContains(response, category.title)
        self.assertContains(response, category.get_absolute_url())

    def test_collectiondetailview(self):
        """ Make sure collection is shown in artwork detail. """

        obj = self.create_artwork()
        obj.save()

        url = obj.get_absolute_url()

        # Attempt request
        response = self.client.get(url)

        # The category title and URL should be in the page, somewhere
        self.assertContains(response, obj.collection.title)
        self.assertContains(response, obj.collection.get_absolute_url())

    def test_context_processors(self):
        """ Test the collections and artworks context processors. """

        obj = self.create_artwork()
        obj.save()

        url = obj.get_absolute_url()
        response = self.client.get(url)

        # Assert 'collections' and 'artworks' are in context
        self.assertIn('collections', response.context)
        self.assertIn('artworks', response.context)
        self.assertIn('categories', response.context)

        self.assertIn(obj, response.context['artworks'])
        self.assertIn(obj.collection, response.context['collections'])

        # Check category context processor
        category = self.create_category()
        category.save()

        self.assertEquals([category, ], list(response.context['categories']))

    def test_sitemap(self):
        """ Test the Artworks sitemap. """

        obj = self.create_artwork()
        obj.save()

        url = reverse('django.contrib.sitemaps.views.sitemap')
        self.assertTrue(url)

        # Attempt request
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, obj.get_absolute_url())
        self.assertContains(response, str(obj.modified.date()))


class PictureTests(PortfolioTestBase):
    """ Tests for Pictures. """

    def test_create(self):
        """ Create and save Picture. """
        obj = self.create_picture()
        unicode(obj)
        obj.save()

    def test_picturedetail(self):
        """ Check for presence of picture title in artwork detail view. """

        obj = self.create_picture()
        obj.save()

        artwork = obj.artwork

        url = artwork.get_absolute_url()

        # Attempt request
        response = self.client.get(url)

        # The title should be in the page, somewhere
        self.assertContains(response, obj.title)

    def test_defaultpicture(self):
        """ Test the default image. """

        obj = self.create_picture()
        obj.save()

        artwork = obj.artwork

        self.assertEquals(artwork.get_default_picture(), obj)


class CategoryTests(PortfolioTestBase):
    """ Tests for Categories. """

    def test_create(self):
        """ Create and save Category. """

        obj = self.create_category()
        unicode(obj)
        obj.save()

    def test_listview(self):
        """ Test requesting the object. """

        obj = self.create_category()
        obj.save()

        url = reverse('category_list')
        self.assertTrue(url)

        # Attempt request
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # The title should be in the page, somewhere
        self.assertContains(response, obj.title)
        self.assertContains(response, obj.get_absolute_url())

    def test_detailview(self):
        """ Test requesting the object. """

        obj = self.create_category()
        obj.save()

        url = obj.get_absolute_url()
        self.assertTrue(url)

        # Make sure the slug is in there
        self.assertIn(str(obj.slug), url)

        # Attempt request
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # The title should be in the page, somewhere
        self.assertContains(response, obj.title)

    def test_artworkdetail(self):
        """ Make sure artworks are listed for category detail. """

        obj = self.create_category()
        obj.save()

        artwork = self.create_artwork()
        artwork.save()

        artwork.categories.add(obj)

        url = obj.get_absolute_url()

        # Attempt request
        response = self.client.get(url)

        # The title should be in the page, somewhere
        self.assertContains(response, artwork.title)
        self.assertContains(response, artwork.get_absolute_url())

    def test_sitemap(self):
        """ Test the Category sitemap. """

        obj = self.create_category()
        obj.save()

        url = reverse('django.contrib.sitemaps.views.sitemap')
        self.assertTrue(url)

        # Attempt request
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, obj.get_absolute_url())


class CollectionTests(PortfolioTestBase):
    """ Tests for Collections. """

    def test_create(self):
        """ Create and save Collection. """

        obj = self.create_collection()
        unicode(obj)
        obj.save()

    def test_listview(self):
        """ Test requesting the object. """

        obj = self.create_collection()
        obj.save()

        url = reverse('collection_list')
        self.assertTrue(url)

        # Attempt request
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # The title should be in the page, somewhere
        self.assertContains(response, obj.title)
        self.assertContains(response, obj.get_absolute_url())

    def test_detailview(self):
        """ Test requesting the object. """

        obj = self.create_collection()
        obj.save()

        url = obj.get_absolute_url()
        self.assertTrue(url)

        # Make sure the slug is in there
        self.assertIn(str(obj.slug), url)

        # Attempt request
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # The title should be in the page, somewhere
        self.assertContains(response, obj.title)

    def test_artworkdetail(self):
        """ Make sure artworks are listed for collection detail. """

        obj = self.create_collection()
        obj.save()

        artwork = self.create_artwork(collection=obj)
        artwork.save()

        url = obj.get_absolute_url()

        # Attempt request
        response = self.client.get(url)

        # The title should be in the page, somewhere
        self.assertContains(response, artwork.title)
        self.assertContains(response, artwork.get_absolute_url())

    def test_sitemap(self):
        """ Test the Collection sitemap. """

        obj = self.create_collection()
        obj.save()

        url = reverse('django.contrib.sitemaps.views.sitemap')
        self.assertTrue(url)

        # Attempt request
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, obj.get_absolute_url())


class EditorTestBase(TestCase):
    def test_rich_text_module(self, expected=None):
        imp.reload(editor)
        module = editor.rich_text_module
        self.assertEquals(module, expected)

    def test_admin(self,
                   expected_widget=None,
                   expected_admin=None,
                   expected_inline=None):
        if not expected_widget:
            from django.forms.widgets import Textarea
            expected_widget = Textarea
        if not expected_admin or not expected_inline:
            from django.contrib.admin import ModelAdmin, StackedInline
            expected_admin = ModelAdmin
            expected_inline = StackedInline
        imp.reload(editor)
        self.assertEquals(editor.EditorWidget.__base__, expected_widget)
        self.assertEquals(editor.EditorAdmin.__base__, expected_admin)
        self.assertEquals(editor.EditorStackedInline.__base__, expected_inline)


class EditorTinyMCETest(EditorTestBase):
    @override_settings(INSTALLED_APPS=settings.INSTALLED_APPS+('tinymce',))
    def test_rich_text_module(self, **kwargs):
        super(EditorTinyMCETest, self).test_rich_text_module(
            expected='tinymce'
        )

    @override_settings(INSTALLED_APPS=settings.INSTALLED_APPS+('tinymce',))
    def test_admin(self, **kwargs):
        from tinymce.widgets import TinyMCE
        super(EditorTinyMCETest, self).test_admin(expected_widget=TinyMCE)


class EditorImperaviTest(EditorTestBase):
    @override_settings(INSTALLED_APPS=settings.INSTALLED_APPS+('imperavi',))
    def test_rich_text_module(self, **kwargs):
        super(EditorImperaviTest, self).test_rich_text_module(
            expected='imperavi'
        )

    @override_settings(INSTALLED_APPS=settings.INSTALLED_APPS+('imperavi',))
    def test_admin(self, **kwargs):
        from imperavi.admin import ImperaviAdmin, \
            ImperaviStackedInlineAdmin, \
            ImperaviWidget
        super(EditorImperaviTest, self).test_admin(
            expected_widget=ImperaviWidget,
            expected_admin=ImperaviAdmin,
            expected_inline=ImperaviStackedInlineAdmin
        )


class PortfolioTagsTest(TestCase):
    """
    Tests for template tags
    """
    def setUp(self):
        self.featured = Collection(title='Featured', slug='featured')
        self.featured.save()
        self.artwork1 = Artwork(collection=self.featured, title='Art 1')
        self.artwork1.save()
        self.artwork2 = Artwork(collection=self.featured, title='Art 2')
        self.artwork2.save()
        self.artwork3 = Artwork(collection=self.featured, title='Art 3')
        self.artwork3.save()
        self.photos = Category(title='Photos', slug='photos')
        self.photos.save()
        self.photos.artworks.add(self.artwork1)

    def test_artworks_tag(self):
        """
        Test portfolio_tags.artworks
        """
        # No params
        self.assertListEqual(list(Artwork.objects.all()), list(portfolio_tags.artworks()))
        # Offset/limit
        self.assertListEqual(list(Artwork.objects.all()[1:]), list(portfolio_tags.artworks(offset=1)))
        self.assertListEqual(list(Artwork.objects.all()[1:2]), list(portfolio_tags.artworks(offset=1, limit=1)))
        self.assertListEqual(list(Artwork.objects.all()[:1000]), list(portfolio_tags.artworks(limit=1000)))
        # Filter by category
        self.assertListEqual(list(Artwork.objects.filter(categories=self.photos)),
                             list(portfolio_tags.artworks(category=self.photos))
        )
        self.assertListEqual(list(Artwork.objects.filter(categories=self.photos)),
                             list(portfolio_tags.artworks(category=self.photos.id))
        )
        self.assertListEqual(list(Artwork.objects.filter(categories=self.photos)),
                             list(portfolio_tags.artworks(category=self.photos.slug))
        )
        # Filter by collection
        self.assertListEqual(list(Artwork.objects.filter(collection=self.featured)),
                             list(portfolio_tags.artworks(collection=self.featured))
        )
        self.assertListEqual(list(Artwork.objects.filter(collection=self.featured)),
                             list(portfolio_tags.artworks(collection=self.featured.id))
        )
        self.assertListEqual(list(Artwork.objects.filter(collection=self.featured)),
                             list(portfolio_tags.artworks(collection=self.featured.slug))
        )

    def test_categories_tag(self):
        """
        Test portfolio_tags.categories
        """
        # No params
        self.assertListEqual(list(Category.objects.all()), list(portfolio_tags.categories()))
        # Offset/limit
        self.assertListEqual(list(Category.objects.all()[1:]), list(portfolio_tags.categories(offset=1)))
        self.assertListEqual(list(Category.objects.all()[1:2]), list(portfolio_tags.categories(offset=1, limit=1)))
        self.assertListEqual(list(Category.objects.all()[:1000]), list(portfolio_tags.categories(limit=1000)))

    def test_collections_tag(self):
        """
        Test portfolio_tags.collections
        """
        # No params
        self.assertListEqual(list(Collection.objects.all()), list(portfolio_tags.collections()))
        # Offset/limit
        self.assertListEqual(list(Collection.objects.all()[1:]), list(portfolio_tags.collections(offset=1)))
        self.assertListEqual(list(Collection.objects.all()[1:2]), list(portfolio_tags.collections(offset=1, limit=1)))
        self.assertListEqual(list(Collection.objects.all()[:1000]), list(portfolio_tags.collections(limit=1000)))
