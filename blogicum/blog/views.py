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


class CategoryListView(ListView):
    """Display the posts of the selected category."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        posts = super().get_queryset()
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return posts.filter(
            is_published=True,
            pub_date__lte=datetime.now(),
            category=self.category,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
