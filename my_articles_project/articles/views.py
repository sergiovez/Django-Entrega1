from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArticleForm, CommentForm, ReviewForm
from .models import Article, Comment, Review, Category, Like, Tag
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
import csv
import json
from django.http import HttpResponse
from .utils import send_notification_email
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.text import slugify


def article_list(request):
    query = request.GET.get('q')
    sort = request.GET.get('sort')

    articles = Article.objects.all().order_by('-created_at')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(author__username__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    if sort == 'comments':
        articles = articles.annotate(num_comments=Count('comments')).order_by('-num_comments')
    elif sort == 'likes':
        articles = articles.order_by('-total_likes')
    else:
        articles = articles.order_by('-created_at')
    
    categories = Category.objects.all()
    
    paginator = Paginator(articles, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "articles/article_list.html", {
        "articles": page_obj,
        "query": query,
        "sort": sort,
        "categories": categories,
    })

@login_required
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    comments = Comment.objects.filter(article=article)
    reviews = Review.objects.filter(article=article)
    user_has_liked = article.user_has_liked_article(request.user) if request.user.is_authenticated else False

    # Obtenemos la review del usuario actual (si existe)
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(article=article, reviewer=request.user).first()

    # Manejo del formulario de review
    if request.method == 'POST' and 'review_submit' in request.POST:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid() and request.user.is_authenticated:
            rating = review_form.cleaned_data['rating']
            comment = review_form.cleaned_data['comment']

            if user_review:
                # Si ya hay review, actualizamos
                user_review.rating = rating
                user_review.comment = comment
                user_review.save()
            else:
                # Si no hay review, creamos nueva
                Review.objects.create(
                    article=article,
                    reviewer=request.user,
                    rating=rating,
                    comment=comment
                )

            return redirect('articles:article_detail', slug=article.slug)
    else:
        review_form = ReviewForm(initial={
            'rating': user_review.rating if user_review else None,
            'comment': user_review.comment if user_review else ''
        })

    # Manejo del formulario de comentarios
    if request.method == 'POST' and 'comment_submit' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid() and request.user.is_authenticated:
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
            send_notification_email(
                subject=f"Nuevo comentario en '{article.title}'",
                message=f"{request.user.username} ha comentado tu artículo:\n\n{comment.content}",
                recipient_list=[article.author.email]
            )
            return redirect('articles:article_detail', slug=article.slug)
    else:
        comment_form = CommentForm()

    context = {
        'article': article,
        'user_has_liked': user_has_liked,
        'comments': comments,
        'reviews': reviews,
        'comment_form': comment_form,
        'review_form': review_form,
        'user_review': user_review,
        'rating_choices': [1, 2, 3, 4, 5],
        'user_review': user_review, 
    }

    return render(request, 'articles/article_detail.html', context)


@login_required
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()

            tags_text = form.cleaned_data["tags_input"]
            tag_names = [t.strip() for t in tags_text.split(",") if t.strip()]

            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                article.tags.add(tag)

            return redirect(article.get_absolute_url())
    else:
        form = ArticleForm()

    return render(request, "articles/article_form.html", {
        "form": form,
        "action": "Crear",
    })


@login_required
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if request.user != article.author:
        return HttpResponseForbidden("No puedes editar un artículo que no es tuyo.")

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('articles:article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/article_edit.html', {'form': form, 'article': article})


@login_required
def article_like(request, slug):
    article = get_object_or_404(Article, slug=slug)
    user = request.user

    like = Like.objects.filter(article=article, user=user).first()
    if like:
        like.delete()  # quitar like si ya existe
    else:
        Like.objects.create(article=article, user=user)  # crear nuevo like

        if article.author.email:  # solo si el autor tiene email
            subject = f"Tu artículo '{article.title}' recibió un nuevo like"
            message = f"Hola {article.author.username},\n\n" \
                      f"El usuario {user.username} ha dado like a tu artículo '{article.title}'.\n\n" \
                      f"¡Revisa tu artículo para ver más detalles!"
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [article.author.email],
                fail_silently=True
            )
    return redirect('articles:article_detail', slug=slug)

@login_required
def export_articles_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="articles.csv"'

    writer = csv.writer(response)
    writer.writerow(['Título', 'Autor', 'Categoría', 'Fecha', 'Contenido'])
    for article in Article.objects.all():
        writer.writerow([article.title, article.author.username, article.category, article.created_at, article.content])

    return response

@login_required
def export_articles_json(request):
    articles = list(Article.objects.values('title', 'author__username', 'category', 'created_at', 'content'))
    response = HttpResponse(json.dumps(articles, default=str), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="articles.json"'
    return response

def article_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(category=category)

    return render(request, "articles/article_list.html", {
        "articles": articles,
        "category": category,
    })

@login_required
def review_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    rating = int(request.POST.get('rating', 0))
    comment = request.POST.get('comment', '').strip()

    if rating < 1 or rating > 5:
        rating = 1 

    review, created = Review.objects.update_or_create(
        article=article,
        reviewer=request.user,
        defaults={'rating': rating, 'comment': comment}
    )

    return redirect('articles:article_detail', slug=slug)