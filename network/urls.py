
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('new', views.new, name='new'),
    path("user/<str:username>", views.user_profile, name='user_profile'),
    path("following", views.following, name='following'),
    path("search", views.search, name='search'),
    path('post/<int:id>', views.post, name='post'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
