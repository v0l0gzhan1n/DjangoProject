from django.urls import path
from .views import (
    ArticleListView,
    ArticleDetailView,
    add_comment,
    add_reaction,
    register_view,
    login_view,
    logout_view
)

urlpatterns = [
    path('', ArticleListView.as_view(), name='article_list'),
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('article/<int:article_id>/comment/', add_comment, name='add_comment'),
    path('article/<int:article_id>/reaction/', add_reaction, name='add_reaction'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),  # Добавьте этот путь
    path('logout/', logout_view, name='logout'),
]