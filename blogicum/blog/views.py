from datetime import datetime

from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import MultipleObjectMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .models import Post, Category
from .forms import PostForm

User = get_user_model()


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        posts = super().get_queryset()
        return posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )


class CategoryListView(ListView):
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
            pub_date__lte=timezone.now(),
            category=self.category,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'


class PostCreateView(CreateView):
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


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.get_object().pk
            }
        )


class PostDeleteView(DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class Profile(DetailView, MultipleObjectMixin):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        object_list = Post.objects.filter(author=self.get_object())
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context


class ProfileUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', 'username')
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={
                'username': self.request.user.username
            }
        )
