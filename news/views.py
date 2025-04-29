from datetime import datetime

from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User  # Добавьте, если нужно
from .models import Article, Category, Comment, Reaction
from .forms import SearchForm, RegisterForm, LoginForm, CommentForm

class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)

        form = SearchForm(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data

            if data['query']:
                queryset = queryset.filter(
                    Q(title__icontains=data['query']) |
                    Q(content__icontains=data['query'])
                )

            if data['category']:
                queryset = queryset.filter(categories=data['category'])

            if data['date_from']:
                queryset = queryset.filter(published_at__gte=data['date_from'])

            if data['date_to']:
                date_to = data['date_to']
                date_to = datetime.combine(date_to, datetime.max.time())
                queryset = queryset.filter(published_at__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET)
        context['categories'] = Category.objects.all()
        context['login_form'] = LoginForm()
        context['register_form'] = RegisterForm()
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        article = self.object
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        context['reaction_types'] = [choice[0] for choice in Reaction.REACTION_CHOICES]
        reaction_counts_qs = (
            article.reactions.values('reaction_type')
            .annotate(count=Count('reaction_type'))
            .order_by('reaction_type')
        )
        context['reaction_counts'] = {
            item['reaction_type']: item['count'] for item in reaction_counts_qs
        }
        context['reaction_choices'] = [
            ('like', '👍'),
            ('love', '❤️'),
            ('laugh', '😂'),
            ('wow', '😮'),
            ('sad', '😢'),
            ('angry', '😡')
        ]
        if self.request.user.is_authenticated:
            context['user_reaction'] = (
                article.reactions.filter(user=self.request.user).first()
            )
        else:
            context['user_reaction'] = (
                article.reactions.filter(user__isnull=True).first()
            )
        context['login_form'] = LoginForm()
        context['register_form'] = RegisterForm()
        article_categories = self.object.categories.all()

        # Получаем другие статьи из тех же категорий, исключая текущую статью
        other_articles = Article.objects.filter(categories__in=article_categories).exclude(
            id=self.object.id).distinct()[:5]
        context['other_articles'] = other_articles
        return context


@login_required
def add_comment(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
            return redirect('article_detail', pk=article.id)
    return redirect('article_list')


def add_reaction(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    reaction_type = request.POST.get('reaction_type')
    user = request.user if request.user.is_authenticated else None

    if reaction_type not in dict(Reaction.REACTION_CHOICES):
        return JsonResponse({'status': 'error', 'message': 'Invalid reaction'}, status=400)

    if user:
        user_reactions = Reaction.objects.filter(article=article, user=user)
    else:
        user_reactions = Reaction.objects.filter(article=article, user__isnull=True)

    if user_reactions.filter(reaction_type=reaction_type).exists():
        user_reactions.filter(reaction_type=reaction_type).delete()
    elif user_reactions.count() >= 3:
        return JsonResponse({
            'status': 'error',
            'message': 'Максимум 3 реакции на новость'
        }, status=400)
    else:
        Reaction.objects.create(
            article=article,
            user=user,
            reaction_type=reaction_type
        )

    reaction_counts = (
        article.reactions.values('reaction_type')
        .annotate(count=Count('reaction_type'))
        .order_by('reaction_type')
    )

    if user:
        user_reactions = list(user_reactions.values_list('reaction_type', flat=True))
    else:
        user_reactions = list(Reaction.objects.filter(article=article, user__isnull=True).values_list('reaction_type', flat=True))

    return JsonResponse({
        'status': 'success',
        'reaction_counts': list(reaction_counts),
        'user_reactions': user_reactions
    })


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': str(form.errors)})
    return redirect('article_list')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({'success': True})
        else:
            print("Form errors:", form.errors)
            if not form.errors:
                errors = "Неверное имя пользователя или пароль"
            else:
                errors = '; '.join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
            return JsonResponse({'success': False, 'errors': errors})
    return redirect('article_list')


def logout_view(request):
    logout(request)
    return redirect('article_list')