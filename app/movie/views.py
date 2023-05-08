import os
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import SearchMovieForm
from .models import Movie, FavoriteMovie
import requests

MOVIES_PER_PAGE = 10


def get_movies(title: str, page: int=1) -> tuple[int, list[dict] | None]: 
    api_key = os.getenv('OMDB_API_KEY')
    url = f'http://www.omdbapi.com/?apikey={api_key}&s={title}&page={page}'
    response = requests.get(url)
    response_json = response.json()
    movies = response_json.get('Search', None)
    total_results = int(response_json.get('totalResults', 1))
    dm = divmod(total_results, MOVIES_PER_PAGE)
    number_of_pages: int = dm[0]
    
    if dm[1] != 0:
        number_of_pages += 1

    return number_of_pages, movies,


@login_required
def search_movie_view(request):
    movies = []
    number_of_pages = 0
    page_number = 0
    title: str = request.GET.get('title')
    
    if title:
        form = SearchMovieForm({'title': title})
        page_number = int(request.GET.get('page', 1))
        
        if form.is_valid():
            title_cleaned = form.cleaned_data['title']
            number_of_pages, movies = get_movies(title_cleaned, page_number)
    else:
        form = SearchMovieForm()
    
    return render(
        request, 
        'index.html', 
        context={
            'form': form, 
            'movies': movies, 
            'title': title,
            'number_of_pages': range(1, number_of_pages + 1), 
            'current_page': page_number,
            'next_page': page_number + 1,
            'previous_page': page_number - 1
        })


def get_movie_detail(movie_id: str) -> dict:
    api_key = os.getenv('OMDB_API_KEY')
    url = f'http://www.omdbapi.com/?apikey={api_key}&i={movie_id}'
    response = requests.get(url)
    return response.json()

@login_required
def add_movie_to_favorities(request, movie_id):
    try:
        user = request.user
        movie = Movie.objects.get(imdb_id=movie_id)
        
        try: 
            old_fm = FavoriteMovie.objects.filter(movie=movie, user=user)
            return redirect(reverse('movies:movie_home'))
        except ObjectDoesNotExist:
            fm = FavoriteMovie(user=user, movie=movie)
            fm.save()
    except ObjectDoesNotExist:
        response = get_movie_detail(movie_id)
        new_movie = Movie(
            title=response.get('Title'),
            year=response.get('Year'),
            genre=response.get('Genre'),
            plot=response.get('Plot'),
            poster=response.get('Poster'),
            metascore=response.get('Metascore'),
            imdb_rating=response.get('imdbRating'),
            imdb_id=response.get('imdbID')
        )
        new_movie.save()
        fm = FavoriteMovie(user=user, movie=new_movie)
        fm.save()
        
    return redirect(reverse('movies:movie_home'))
    

@login_required
def get_user_movies_view(request):
    user = request.user
    favorite_movies = FavoriteMovie.objects.filter(user=user)
    movies = Movie.objects.filter(favoritemovie__in=favorite_movies)
    paginator = Paginator(movies, MOVIES_PER_PAGE)
    page_number = request.GET.get('page')
    movies_pag = paginator.get_page(page_number)
    
    return render(request, 'list.html', context={'movies': movies_pag})


@login_required
def remove_movie_from_favorities(request, movie_id):
    try:
        user = request.user
        movie = Movie.objects.get(imdb_id=movie_id)
        FavoriteMovie.objects.filter(user=user, movie=movie).delete()
        return redirect(reverse('movies:movie_list_favorite'))
    except ObjectDoesNotExist:
        return HttpResponse('Given movies does not exist!')
