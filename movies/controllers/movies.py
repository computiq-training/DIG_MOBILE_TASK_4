from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic.types import UUID4
from ninja.pagination import paginate, PageNumberPagination

from account.authorization import TokenAuthentication
from movies.models import Movie
from movies.schemas.Favorite import FavOut
from movies.schemas.movies import MovieOut
from utils.schemas import MessageOut
from ninja.pagination import RouterPaginated

router = RouterPaginated()
User = get_user_model()
movies_controller = Router(tags=['Movies'])


@movies_controller.get('{page}', response={200: list[MovieOut], 404: MessageOut})
def list_movies(request, page: int):
    movies = Movie.objects.prefetch_related('categories', 'movie_actors').all()
    p_movies = Paginator(movies, 3)
    page_movies = p_movies.get_page(page)

    if movies:
        return 200, page_movies.object_list
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
    return 404, {'msg': 'There are no favorites movies.'}



@movies_controller.get('/{id}', response={200: MovieOut, 404: MessageOut})
def get_movie(request, id: UUID4):
    try:
        movie = Movie.objects.get(id=id)
        return 200, movie
    except Movie.DoesNotExist:
        return 404, {'msg': 'There is no movie with that id.'}



@movies_controller.post('/favorites/{id}', auth=TokenAuthentication(), response={200: MessageOut, 404: MessageOut})
def add_favorite_movies(request, id: UUID4):
    try:
        user = User.objects.get(id=request.auth['id'])
        fav_movie = Movie.objects.get(id=id)

        #if fav_movie is already added send message
        if Movie.objects.filter(user__id= user.id, id= id):
            return 200, {'msg': 'this movie already added to favorites'}

        fav_movie.user.add(user)
        return 200, {'msg': 'added to favorites'}

    except Movie.DoesNotExist:
        return 404, {'msg': 'there is no movie with this id'}



@movies_controller.delete('/favorites/{id}', auth=TokenAuthentication(), response={200: MessageOut, 404: MessageOut})
def add_favorite_movies(request, id: UUID4):
    try:
        user = User.objects.get(id=request.auth['id'])
        fav_movie = Movie.objects.get(id=id)

        #if fav_movie is already added send message
        if Movie.objects.filter(user__id= user.id, id= id):
            fav_movie.user.remove(user)
            return 200, {'msg': 'removed from favorites'}


        return 200, {'msg': 'this movie is not in favorites'}

    except Movie.DoesNotExist:
        return 404, {'msg': 'there is no movie with this id'}


