from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('create/', views.article_create, name='article_create'),
    path('<slug:slug>/edit/', views.article_edit, name='article_edit'),
    path("<slug:slug>/", views.article_detail, name="article_detail"),
    path('<slug:slug>/like/', views.article_like, name='article_like'),
    path('export/csv/', views.export_articles_csv, name='export_csv'),
    path('export/json/', views.export_articles_json, name='export_json'),
    path("category/<slug:slug>/", views.article_by_category, name="articles_by_category"),
    path('<slug:slug>/review/', views.review_article, name='review_article'),

]
