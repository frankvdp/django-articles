from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed

from articles.models import Article

# default to 24 hours for feed caching
FEED_TIMEOUT = getattr(settings, 'ARTICLE_FEED_TIMEOUT', 86400)


class LatestEntries(Feed):

    def title(self):
        return "%s Articles" % ('Foobar')

    def link(self):
        return reverse('articles_archive')

    def items(self):
        key = 'latest_articles'
        articles = cache.get(key)

        if articles is None:
            articles = list(
                Article.objects.live().order_by('-publish_date')[:15])
            cache.set(key, articles, FEED_TIMEOUT)

        return articles

    def item_author_name(self, item):
        return item.author.username

    def item_pubdate(self, item):
        return item.publish_date


class LatestEntriesAtom(LatestEntries):
    feed_type = Atom1Feed
