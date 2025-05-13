from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        'pages/',
        include('pages.urls')
    ),
    path(
        '',
        include('blog.urls')
    ),
]

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_errors'
