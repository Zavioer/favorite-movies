from django.urls import path
import movie.views as views

app_name = 'movies'

urlpatterns = [
    path('movies', views.search_movie_view, name='movie_home'),
    path('movies/favorite/', views.get_user_movies_view, name='movie_list_favorite'),
    path('movies/add/to/favorities/<str:movie_id>', views.add_movie_to_favorities, name='movie_add_to_favorite'),
    path('movies/remove/from/favorities/<str:movie_id>', views.remove_movie_from_favorities, name='remove_movie_from_favorite'),
]
