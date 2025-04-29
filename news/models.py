from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    full_content = models.TextField(blank=True)  # Добавляем поле для полного текста
    url = models.URLField()
    published_at = models.DateTimeField(default=timezone.now)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def get_reaction_counts(self):
        counts = self.reactions.values('reaction_type').annotate(count=Count('reaction_type'))
        return {item['reaction_type']: item['count'] for item in counts}

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_at']


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😡')
    ]

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['article', 'user', 'reaction_type'],
                name='unique_reaction_per_user',
                condition=models.Q(user__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['article', 'reaction_type'],
                name='unique_reaction_for_anonymous',
                condition=models.Q(user__isnull=True)
            )
        ]


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']