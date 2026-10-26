
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),

    path('post/create/', views.create_post, name='create_post'),
    path('ai-write/', views.ai_write_post, name='ai_write_post'),

    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/like/', views.toggle_like, name='toggle_like'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),

    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('post/<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),

    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='home'),
        name='logout'
    ),
]


    

