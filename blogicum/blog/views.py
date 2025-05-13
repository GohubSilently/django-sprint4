from datetime import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse

from .models import Post, Category
from .forms import PostForm

User = get_user_model()

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


class PostDetailView(DetailView):
    """Display the selected post."""

    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'


class PostCreateView(CreateView):
    """Create post."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.is_published = True
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.request.user.username
            }
        )
