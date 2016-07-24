import logging

from django import forms
from .models import Article

log = logging.getLogger('articles.forms')


class ArticleAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """Sets the list of tags to be a string"""

        instance = kwargs.get('instance', None)
        if instance:
            init = kwargs.get('initial', {})
            kwargs['initial'] = init

        super(ArticleAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Article
        fields = '__all__'

    class Media:
        css = {
            'all': ('articles/css/jquery.autocomplete.css',),
        }
        js = (
            'articles/js/jquery-1.4.1.min.js',
            'articles/js/jquery.bgiframe.min.js',
            'articles/js/jquery.autocomplete.pack.js',
            'articles/js/tag_autocomplete.js',
        )
