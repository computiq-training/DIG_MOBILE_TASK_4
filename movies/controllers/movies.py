from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic.types import UUID4
import requests
from ninja.pagination import paginate
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.shortcuts import render
from account.authorization import TokenAuthentication,HttpBearer
from movies.models import Movie
from movies.schemas.movies import MovieOut
from utils.schemas import MessageOut

User = get_user_model()

movies_controller = Router(tags=['Movies'])


@movies_controller.get('page_number', response={200: list[MovieOut], 404: MessageOut})
def list_movies(request, page_number):
    movies = Movie.objects.all().order_by('title')
    page_numbers = request.GET.get('page_number')
    paginator = Paginator(movies, 3)
    movies = paginator.get_page(page_number)
    try :
        if movies.object_list:
            return 200, movies.object_list
    except page_numbers.EmptyPage:
        return 404, {'msg': 'this is empty page.'}


@movies_controller.get('/featured', response={200: list[MovieOut], 404: MessageOut})
def featured_movies(request):
    movies = Movie.objects.filter(is_featured=True).order_by('-rating')
    if movies:
        return 200, movies
    return 404, {'msg': 'There are no featured movies.'}


@movies_controller.get('/favorites', auth=TokenAuthentication(), response={200: list[MovieOut], 404: MessageOut})
def favorite_movies(request):
    movies = Movie.objects.filter(user__exact=request.auth['id']).order_by('-rating')
    if movies:
        return 200, movies
    return 404, {'msg': 'There are no featured movies.'}


@movies_controller.get('/{id}', response={200: MovieOut, 404: MessageOut})
def get_movie(request, id: UUID4):
    try:
        movie = Movie.objects.get(id=id)
        return 200, movie
    except Movie.DoesNotExist:
        return 404, {'msg': 'There is no movie with that id.'}


@movies_controller.post('/favorites/{id}', auth=TokenAuthentication(),response={201: MessageOut, 400: MessageOut})
def favorite_movie(request, id: UUID4):
    movies = get_object_or_404(Movie, id=id)
    user=get_object_or_404(User,id=requests.auth['id'])
    movies.user.add(user)
    return 200, {'msg': 'add to favourite successfully.'}



@movies_controller.delete('/favorites/{id}', auth=TokenAuthentication(),response={201: MessageOut, 400: MessageOut})
def favorite_movie(request, id: UUID4):
    movies = get_object_or_404(Movie, id=id)
    user=get_object_or_404(User,id=requests.auth['id'])
    movies.user.remove(user)
    return 200,{'msg': 'delete from favourite successfully.'}



