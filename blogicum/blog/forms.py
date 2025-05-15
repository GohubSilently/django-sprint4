from django import forms


from .models import Post


class PostForm(forms.ModelForm):
    """Form to create post."""

    class Meta:
        model = Post
        exclude = ('is_published', 'author', )
        widgets = {
            'pub_date': forms.DateTimeInput(
                format=('%Y-%m-%dT%H:%M'),
                attrs={
                    'type': 'datetime-local'
                }
            )
        }