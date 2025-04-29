from django.contrib import admin
from .models import Article, Category, Source

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_at', 'is_active')
    list_filter = ('is_active', 'source', 'categories')
    search_fields = ('title', 'content')
    filter_horizontal = ('categories',)

admin.site.register(Article, ArticleAdmin)
admin.site.register(Category)
admin.site.register(Source)