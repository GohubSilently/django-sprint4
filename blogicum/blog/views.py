from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User


POSTS_ON_PAGE = 10


class PostMixin:
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={
                'post_id': self.kwargs['post_id']
            }
        )


def get_posts(
    posts=Post.objects.all(),
    select_related=True,
    filter=True,
    count_comment=True,
):
    if select_related:
        posts = posts.select_related('author', 'location', 'category')
    if filter:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
    if count_comment:
        posts = posts.annotate(
            comment_count=Count('comments')).order_by('-pub_date')
    return posts


def paginate_posts(request, queryset, per_page=None):
    return Paginator(queryset, per_page).get_page(request.GET.get('page'))


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_ON_PAGE

    queryset = get_posts()


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_ON_PAGE

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return get_posts(self.get_category().posts.all())

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            category=self.get_category()
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author == self.request.user:
            return post
        return super().get_object(get_posts(
            select_related=False, count_comment=False
        ))

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


class PostUpdateView(PostMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.kwargs[self.pk_url_kwarg]]
        )


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    success_url = reverse_lazy('blog:index')


class Profile(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    paginate_by = POSTS_ON_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object
        posts = get_posts(
            author.posts.all(),
            filter=self.request.user != author)

        context['page_obj'] = paginate_posts(
            self.request, posts, self.paginate_by
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
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
        return reverse(
            'blog:post_detail',
            args=[self.kwargs['post_id']]
        )


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            comment=self.get_object()
        )


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass
