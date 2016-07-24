from datetime import datetime
import logging

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from autoslug import AutoSlugField

log = logging.getLogger('articles.models')


def get_name(user):
    """
    Provides a way to fall back to a user's username if their full name has not
    been entered.
    """

    key = 'username_for_%s' % user.id

    log.debug('Looking for "%s" in cache (%s)' % (key, user))
    name = cache.get(key)
    if not name:
        log.debug('Name not found')

        if len(user.get_full_name().strip()):
            log.debug('Using full name')
            name = user.get_full_name()
        else:
            log.debug('Using username')
            name = user.username

        log.debug('Caching %s as "%s" for a while' % (key, name))
        cache.set(key, name, 86400)

    return name
User.get_name = get_name


class ArticleStatusManager(models.Manager):

    def default(self):

        default = self.all()[:1]

        if len(default) == 0:

            return None

        else:

            return default[0]


class ArticleStatus(models.Model):

    name = models.CharField(max_length=50)
    ordering = models.IntegerField(default=0)
    is_live = models.BooleanField(default=False, blank=True)

    # TODO fix for deault
    # objects = ArticleStatusManager()

    class Meta:
        ordering = ('ordering', 'name')
        verbose_name_plural = _('Article statuses')

    def __str__(self):

        if self.is_live:
            return '%s (live)' % self.name
        else:
            return self.name


class ArticleManager(models.Manager):

    def live(self, user=None, **kwargs):

        now = datetime.now()

        return self.get_queryset().filter(
            Q(expiration_date__isnull=True) |
            Q(expiration_date__gte=now),
            publish_date__lte=now,
            is_active=True)

    def active(self):
        """
        Retrieves all active articles which have been published and have not
        yet expired.
        """

        now = datetime.now()

        return self.get_queryset().filter(
            Q(expiration_date__isnull=True) |
            Q(expiration_date__gte=now),
            publish_date__lte=now,
            is_active=True)


class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='title', unique=True)
    status = models.ForeignKey(
        ArticleStatus)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)

    keywords = models.TextField(blank=True, help_text=_(
        "If omitted, the keywords will be the same as the article tags."))
    description = models.TextField(blank=True, help_text=_(
        "If omitted, the description will be determined by the first "
        "bit of the article's content."))

    content = models.TextField()

    publish_date = models.DateTimeField(
        default=datetime.now,
        help_text=_(
            'The date and time this article shall appear online.'))
    expiration_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_(
            'Leave blank if the article does not expire.'))

    is_active = models.BooleanField(default=True, blank=True)
    login_required = models.BooleanField(blank=True, help_text=_(
        'Enable this if users must login before they can read this article.'))

    objects = ArticleManager()

    def __str__(self):

        return self.title

    @models.permalink
    def get_absolute_url(self):

        return ('articles_display_article',
                (self.publish_date.year, self.slug))

    class Meta:

        ordering = ('-publish_date', 'title')
        get_latest_by = 'publish_date'
