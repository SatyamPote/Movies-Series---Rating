from django import forms

class MovieFilterForm(forms.Form):
    title = forms.CharField(required=False, label="Title Contains")
    genre = forms.CharField(required=False, label="Genre Contains")
    language = forms.CharField(required=False, label="Language")
    min_rating = forms.FloatField(required=False, label="Minimum Rating")
    release_year = forms.IntegerField(required=False, label="Release Year")

class SeriesFilterForm(forms.Form):
    title = forms.CharField(required=False, label="Title Contains")
    genre = forms.CharField(required=False, label="Genre Contains")
    language = forms.CharField(required=False, label="Language")
    min_rating = forms.FloatField(required=False, label="Minimum Rating")
    first_air_year = forms.IntegerField(required=False, label="First Air Year")

class SearchForm(forms.Form):
    search_term = forms.CharField(label="Movie or Series Title", widget=forms.Textarea(attrs={'rows': 1, 'cols': 40}))  # Textarea for input