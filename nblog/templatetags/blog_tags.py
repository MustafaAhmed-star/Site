from django import template
from ..models import Post
from django.db.models import Count
register= template.Library()
#a simple template tag 
@register.simple_tag
def total_posts():
    return Post.published.count()

#a inclusion template tag
@register.inclusion_tag('nblog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts= Post.published.order_by('-publish')[:count]
    return {'latest_posts':latest_posts}

#a template tag with querysets
@register.simple_tag 
def get_most_commented_posts(count=3):
    return Post.published.annotate(
                        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]
