from django import forms
from .models import Article, Comment, Review, Tag

class ArticleForm(forms.ModelForm):
    tags_input = forms.CharField(required=False, help_text="Separar por comas (ej: python, IA, backend)")
    class Meta:
        model = Article
        fields = ['title', 'content', 'category','tags_input','slug'] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del artículo'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Contenido del artículo', 'rows': 6}),
            'tags': forms.CheckboxSelectMultiple(),
            'category': forms.Select(),        
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Slug único'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if ' ' in slug:
            raise forms.ValidationError("El slug no puede contener espacios.")
        return slug


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content'] 
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu comentario','rows': 3}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }