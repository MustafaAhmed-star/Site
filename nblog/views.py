from django.shortcuts import render,get_object_or_404
from .models import Post,Comment
from django.http import Http404
from django.core.paginator import Paginator,EmptyPage,\
                                                        PageNotAnInteger
from django.views.generic import ListView
 
from .forms import EmailPostForm ,CommentForm,SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, \
                                           SearchQuery, SearchRank ,TrigramSimilarity
# Create your views here.
def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                 'nblog/post/list.html',
                 {'posts': posts,
                  'tag': tag})
"""
def post_list(request):
    post_list=Post.published.all()
    #paginators 
    paginator=Paginator(post_list,3)
    page_number=request.GET.get('page', 1)
    try:
        posts=paginator.page(page_number)
    except PageNotAnInteger:
        posts=paginator.page(1)    
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)    
    context={
        'posts':posts,
    }
    return render(request,'nblog/post/list.html',context=context)
"""
#class PostListView(ListView):
    #queryset=Post.published.all()
    #context_object_name='posts'
    #paginate_by=3
    #template_name='nblog/post/list.html'
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    #List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                 .order_by('-same_tags','-publish')[:4]
    context={
        'post':post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts,
    }
    
    return render(request,'nblog/post/detail.html',context=context)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'kkamen24@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    context = {
        'post': post,
        'form': form,
        'sent': sent,
    }
    return render(request, 'nblog/post/share.html', context=context)


@require_POST
def post_comment(request,post_id):
    post=get_object_or_404(Post,
                           id=post_id,
                           status=Post.Status.PUBLISHED)
    comment=None
    form=CommentForm(data=request.POST)
    if form.is_valid():
        comment=form.save(commit=False)
        comment.post=post
        comment.save()
    context = {
        'post': post,
        'form': form,
        'comment': comment,
    }
    return render(request,'nblog/post/comment.html',context=context)

def post_search(request):
    form=SearchForm()
    query=None
    results=[]
    if 'query' in request.GET:
        form= SearchForm(request.GET)
        if form.is_valid():
            query=form.cleaned_data['query']
            search_vector = SearchVector('title',weight='A')+\
                            SearchVector('body', weight='B')
            search_query = SearchQuery(query)

            results= Post.published.annotate(  similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
                #search=search_vector,rank=SearchRank(search_vector,search_query
                   # ).filter(rank__gte=0.3).order_by('-rank')
                    
    context={
        'form': form,
        'query': query,
        'results': results
    }
    return render(request,'nblog/post/search.html',context=context)