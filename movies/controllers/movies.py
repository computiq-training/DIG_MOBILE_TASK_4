from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic.types import UUID4

from account.authorization import TokenAuthentication
from movies.models import Movie
from movies.schemas.movies import MovieOut
from utils.schemas import MessageOut

from django.core.paginator import Paginator
User = get_user_model()

movies_controller = Router(tags=['Movies'])


@movies_controller.get('{pagi_num}/', response={200: list[MovieOut], 404: MessageOut})
def list_movies(request,pagi_num:int):
    movies = Movie.objects.prefetch_related('categories', 'movie_actors').all()
    paginatr = Paginator(movies, 2)

    if movies:
        return 200, movies
    
    movies = paginatr.get_page(pagi_num)
    if movies.object_list:
        return 200, movies.object_list

    return 404, {'msg': 'There are no movies yet.'}


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





@movies_controller.delete('/favorites/{id}', auth=TokenAuthentication(), response={200: MessageOut, 404: MessageOut})
def Delete_from_favorate(request, id: UUID4):
    try:

        user = User.objects.get(id=request.auth['id'])
        fav_movie = Movie.objects.get(id=id)

        if Movie.objects.filter(user__id=user.id, id=id):
            fav_movie.user.remove(user)
            return 200, {'msg': 'Movie deleted successfully'}

        else:
            return 404, {'msg': 'ThIS movie did not found in your favorite list'}

    except:
        return 404, {'msg': 'ERORR!'}



@movies_controller.post('/favorites/{id}',auth=TokenAuthentication(),response={200: MessageOut,404: MessageOut})
def Add_to_favorate(request, id: UUID4):

    try:
        user = User.objects.get(id=request.auth['id'])
        fav_movie = Movie.objects.get(id=id)

        if Movie.objects.filter(user__id=user.id, id=id):
            return 200, {'msg': 'This movie is in your favorite list'}

        else:
            fav_movie.user.add(user)
            return 200, {'msg': 'Movie added successfully!'}

    except:
        return 404, {'msg': 'ERORR!'}