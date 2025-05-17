from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.list import MultipleObjectMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post, User


POSTS_ON_PAGE = 10


class CommentSetting:
    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != self.request.user:
            raise Http404(
                'Вы не можете редактировать/удалить чужой комментарий!'
            )
        return comment

    def get_success_url(self):
        comment = self.get_object()
        return reverse(
            'blog:post_detail',
            kwargs={
                'post_id': comment.post.pk
            }
        )


def get_published_posts(queryset):
    return queryset.select_related('author', 'location', 'category').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def add_comment_count(posts):
    for post in posts:
        post.comment_count = post.comments.count()
    return posts


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        posts = get_published_posts(super().get_queryset())
        return add_comment_count(posts)


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        queryset = super().get_queryset().filter(category=self.category)
        posts = get_published_posts(queryset)
        return add_comment_count(posts)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, category=self.category)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author == self.request.user:
            return post

        posts = get_published_posts(self.get_queryset())
        if not posts.filter(pk=post.pk):
            raise Http404('Пост не найден или не опубликован')
        return post

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=CommentForm(),
            comments=self.object.comments.all()
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user:
            return redirect('blog:post_detail', post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.kwargs['post_id']]
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user:
            raise Http404('Вы не можете удалять чужие посты!')
        return post


class Profile(DetailView, MultipleObjectMixin):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    paginate_by = POSTS_ON_PAGE

    def get_posts_queryset(self):
        author = self.get_object()
        if self.request.user == author:
            posts = author.posts.select_related(
                'category', 'location', 'author'
            ).all()
        else:
            posts = get_published_posts(author.posts.all())
        return add_comment_count(posts)

    def get_context_data(self, **kwargs):
        posts = self.get_posts_queryset()
        return super().get_context_data(object_list=posts, **kwargs)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', 'username')
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            args=[self.kwargs['post_id']]
        )


class CommentUpdateView(LoginRequiredMixin, CommentSetting, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            comment=self.get_object(),
            post=self.post
        )


class CommentDeleteView(LoginRequiredMixin, CommentSetting, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
