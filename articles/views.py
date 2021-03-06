import logging

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.http import (
    HttpResponsePermanentRedirect, Http404, HttpResponseRedirect)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from articles.models import Article
from datetime import datetime

ARTICLE_PAGINATION = getattr(settings, 'ARTICLE_PAGINATION', 20)

log = logging.getLogger('articles.views')


def display_blog_page(
        request, tag=None, username=None, year=None, month=None, page=1):
    """
    Handles all of the magic behind the pages that list articles in any way.
    Yes, it's dirty to have so many URLs go to one view, but I'd rather do that
    than duplicate a bunch of code.  I'll probably revisit this in the future.
    """

    context = {'request': request}
    if username:
        # listing articles by a particular author
        user = get_object_or_404(get_user_model(), name=username)
        articles = user.article_set.live(user=request.user)
        template = 'articles/by_author.html'
        context['author'] = user

    elif year and month:
        # listing articles in a given month and year
        year = int(year)
        month = int(month)
        articles = Article.objects.live(
            user=request.user).select_related().filter(
            publish_date__year=year, publish_date__month=month)
        template = 'articles/in_month.html'
        context['month'] = datetime(year, month, 1)

    else:
        # listing articles with no particular filtering
        articles = Article.objects.live(user=request.user)
        template = 'articles/article_list.html'

    # paginate the articles
    paginator = Paginator(articles, ARTICLE_PAGINATION,
                          orphans=int(ARTICLE_PAGINATION / 4))
    try:

        page = paginator.page(page)

    except EmptyPage:

        raise Http404

    context.update({'paginator': paginator,
                    'page_obj': page})
    variables = RequestContext(request, context)
    response = render_to_response(template, variables)

    return response


def display_article(
        request, year, slug, template='articles/article_detail.html'):
    """Displays a single article."""

    try:
        article = Article.objects.live(
            user=request.user).get(publish_date__year=year, slug=slug)
    except Article.DoesNotExist:
        raise Http404

    # make sure the user is logged in if the article requires it
    if article.login_required and not request.user.is_authenticated():
        return HttpResponseRedirect(
            reverse('auth_login') + '?next=' + request.path)

    variables = RequestContext(request, {
        'article': article,
        'disqus_forum': getattr(settings, 'DISQUS_FORUM_SHORTNAME', None),
    })
    response = render_to_response(template, variables)

    return response


def redirect_to_article(request, year, month, day, slug):
    # this is a little snippet to handle URLs that are formatted the old way.
    article = get_object_or_404(Article, publish_date__year=year, slug=slug)
    return HttpResponsePermanentRedirect(article.get_absolute_url())
