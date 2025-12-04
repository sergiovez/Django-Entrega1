from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Avg


# Create your models here.

class Category(models.Model):
    """
    Modelo que representa una categoría de artículos.
    Ej: Tecnología, Salud, Educación, etc.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('articles:article_list') + f'?category={self.id}'
    

class Tag(models.Model):
    """
    Modelo que representa una etiqueta para artículos.
    Ej: Python, Django, Fitness, Recetas
    """
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Modelo que representa un artículo publicado en la plataforma.
    """
    title = models.CharField(max_length=200)  
    content = models.TextField()
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('articles:article_detail', kwargs={'slug': self.slug})

    def total_likes(self):
        return self.likes.count()
    
    def user_has_liked_article(self, user):
        return self.likes.filter(user=user).exists()
    
    def average_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg']

class Comment(models.Model):
    """
    Modelo que representa un comentario en un artículo.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True) 

    def __str__(self):
        return f'Comentario de {self.user} en {self.article}'


class Review(models.Model):
    """
    Modelo que representa la revisión de un artículo.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False) 

    class Meta:
        unique_together = ('article', 'reviewer')

    def __str__(self):
        return f'Review de {self.reviewer} sobre {self.article}'


class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('article', 'user')