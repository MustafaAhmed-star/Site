from django.shortcuts import render,get_object_or_404
from .models import Post
from django.http import Http404
# Create your views here.
def post_list(request):
    posts=Post.published.all()
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