from django.views.generic import TemplateView
from django.shortcuts import render


class AboutTemplateView(TemplateView):
    """Display the page 'О проекте'."""

    template_name = 'pages/about.html'


class RulesTemplateView(TemplateView):
    """Display the page 'Наши правила'."""

    template_name = 'pages/rules.html'


def csrf_failure(request, reason=''):
    """ERROR 403."""
    return render(
        request,
        'pages/403csrf.html',
        status=403
    )


def page_not_found(request, exception):
    """ERROR 404."""
    return render(
        request,
        'pages/404.html',
        status=404
    )


def server_errors(request):
    """ERROR 500."""
    return render(
        request,
        'pages/500.html',
        status=500
    )
