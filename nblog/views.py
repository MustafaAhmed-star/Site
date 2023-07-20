from django.shortcuts import render,get_object_or_404
from .models import Post
from django.http import Http404
from django.core.paginator import Paginator,EmptyPage,\
                                                        PageNotAnInteger
# Create your views here.
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

def post_detail(request,year,month,day,post):
    post=get_object_or_404(Post,
                           status=Post.Status.PUBLISHED,
                           slug=post,
                           publish__year=year,
                           publish__month=month,
                           publish__day=day,)
    context={
        'post':post,
    }
    
    return render(request,'nblog/post/detail.html',context=context)