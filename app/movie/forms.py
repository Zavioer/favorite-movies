from django import forms


class SearchMovieForm(forms.Form):
    title = forms.CharField(label='Movie title', max_length=255)
