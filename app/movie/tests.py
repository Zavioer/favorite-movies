from django.test import TestCase
from django.contrib.auth.models import User
from unittest import mock
from django.urls import reverse
from .models import Movie, FavoriteMovie


# Create your tests here.
class SearchMovieViewTestCase(TestCase):
    def setUp(self) -> None:
        user = User.objects.create(username='a', password='a')
        self.client.force_login(user)
    
    @mock.patch('movie.views.get_movies')
    def test_get_correct_movie(self, mock_get):
        movies = [
                {'Title': 'Mock movie', 'imdbID': '1'}
            ]
        number_of_pages = 1
        mock_get.return_value = tuple([number_of_pages, movies])
        response = self.client.get(reverse('movies:movie_home'), {'title': 'test'})
        
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['movies'], movies)
        self.assertEqual(response.context['number_of_pages'], range(1, number_of_pages + 1))
        
    
class AddMovieToFavoritesTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='a', password='a')
        self.client.force_login(self.user)
    
    @mock.patch('movie.views.get_movie_detail')
    def test_add_movie_to_db_only_once(self, mmock):
        imdb_id = 'testId1'
        movie = {
            'Title': 'Mock movie',
            'Year': 2023,
            'Genre': 'Action, Family, Horror',
            'Plot': '...',
            'Poster': None,
            'Metascore': 100,
            'imdbRating': 0,
            'imdbID': imdb_id
        }
        
        mmock.return_value = movie
        self.client.get(reverse('movies:movie_add_to_favorite', kwargs={'movie_id': imdb_id}))
        response = self.client.get(reverse('movies:movie_add_to_favorite', kwargs={'movie_id': imdb_id}))
      
        self.assertEqual(Movie.objects.filter(imdb_id=imdb_id).count(), 1)
        self.assertEqual(FavoriteMovie.objects.filter(user=self.user).count(), 1)
        
        
class RemoveMovieFromFavoritesTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='a', password='a')
        self.client.force_login(self.user)
        
    def test_if_movie_removes_correct_from_favorites(self):
        imdb_id = '1234'
        movie = {
            'title': 'Mock movie',
            'year': 2023,
            'genre': 'Action, Family, Horror',
            'plot': '...',
            'poster': None,
            'metascore': 100,
            'imdb_rating': 0,
            'imdb_id': imdb_id
        }
        
        movie_obj = Movie.objects.create(**movie)
        FavoriteMovie.objects.create(user=self.user, movie=movie_obj)
        
        self.client.get(reverse('movies:remove_movie_from_favorite', kwargs={'movie_id': imdb_id}))
        
        self.assertEqual(FavoriteMovie.objects.filter(user=self.user).count(), 0)
        
    def test_correct_response_if_movies_does_not_exist(self):
        response = self.client.get(reverse('movies:remove_movie_from_favorite', kwargs={'movie_id': 'xxxx'}))
        self.assertEqual(response.content.decode('utf-8'), 'Given movies does not exist!')
