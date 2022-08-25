from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("view/<str:listing_id>", views.view_listing, name="view_listing"),
    path("close/<str:listing_id>", views.close_listing, name="close_listing"),
    path("watch", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("category/<str:name>", views.view_category, name="category")
]