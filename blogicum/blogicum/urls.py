from django.contrib.auth.forms import UserCreationForm
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic.edit import CreateView
from django.urls import path, include, reverse_lazy
from .views import CustomLogoutView


urlpatterns = [
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        'auth/logout/',
        CustomLogoutView.as_view(),
        name='logout'
    ),
    path(
        'auth/',
        include('django.contrib.auth.urls')
    ),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index')
        ),
        name='registration'
    ),
    path(
        'pages/',
        include('pages.urls')
    ),
    path(
        '',
        include('blog.urls')
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_errors'
