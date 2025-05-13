from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from . models import Post, Category


class PostListView(ListView):
    """Display the Homepage."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        posts = super().get_queryset()
        return posts.filter(
            is_published=True,
            pub_date__lte=datetime.now()
        )
