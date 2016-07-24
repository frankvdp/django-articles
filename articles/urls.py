# from django.conf.urls.defaults import *
from django.conf.urls import url, patterns
from articles import views
from articles.feeds import LatestEntries, LatestEntriesAtom

latest_rss = LatestEntries()
latest_atom = LatestEntriesAtom()

urlpatterns = patterns(
    '',
    (r'^(?P<year>\d{4})/(?P<month>.{3})/(?P<day>\d{1,2})/(?P<slug>.*)/$',
        views.redirect_to_article),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/page/(?P<page>\d+)/$',
        views.display_blog_page, name='articles_in_month_page'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        views.display_blog_page, name='articles_in_month'),
)

urlpatterns += patterns(
    '',
    url(r'^$', views.display_blog_page,
        name='articles_archive'),
    url(r'^page/(?P<page>\d+)/$', views.display_blog_page,
        name='articles_archive_page'),

    url(r'^author/(?P<username>.*)/page/(?P<page>\d+)/$',
        views.display_blog_page, name='articles_by_author_page'),
    url(r'^author/(?P<username>.*)/$',
        views.display_blog_page, name='articles_by_author'),

    url(r'^(?P<year>\d{4})/(?P<slug>.*)/$',
        views.display_article, name='articles_display_article'),

)
