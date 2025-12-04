from django.contrib import admin

# Register your models here.
from .models import Article, Category, Tag

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category","created_at")
    list_filter = ("author", "category")
    search_fields = ("title", "author", "content")
    ordering = ("-created_at",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('name',)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display=('name',)