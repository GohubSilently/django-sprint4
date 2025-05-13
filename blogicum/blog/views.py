from datetime import datetime

from django.shortcuts import render, get_object_or_404

from . models import Post, Category


def published_posts(queryset=Post.objects):
    return queryset.select_related(
        'category', 'author', 'location'
    ).filter(
        pub_date__lte=datetime.now(),
        is_published=True,
        category__is_published=True
    )


def index(request):
    return render(
        request,
        'blog/index.html',
        {'posts': published_posts()[0:5]}
    )


def post_detail(request, post_id):
    return render(
        request,
        'blog/detail.html',
        {'post': get_object_or_404(published_posts(), pk=post_id)})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = published_posts(category.posts)

    return render(request, 'blog/category.html', {
        'category': category,
        'posts': posts,
    })
