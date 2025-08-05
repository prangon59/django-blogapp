from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('post/<slug:slug>/', views.post_page, name='post_page'),
    path('tags/<slug:slug>/', views.tag_page, name='tag_page'),
    path('author/<slug:slug>/', views.author_page, name='author_page'),
    path('search/', views.search_page, name='search_page'),
    path('about/', views.about_page, name='about_page'),
    path('accounts/registration/', views.registration_page, name='registration_page'),
    path('bookmarked_post/<slug:slug>', views.bookmarked_post, name='bookmarked_post'),
    path('liked_post/<slug:slug>', views.liked_post, name='liked_post'),
    path('all_bookmarked_posts/', views.all_bookmarked_posts, name='all_bookmarked_posts'),
    path('all_posts/', views.all_posts, name='all_posts'),
    path('all_liked_posts/', views.all_liked_posts, name='all_liked_posts'),
]
