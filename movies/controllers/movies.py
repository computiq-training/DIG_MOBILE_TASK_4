from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja.pagination import paginate, PageNumberPagination
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from ninja import Router
from pydantic.types import UUID4
from django.core.paginator import Paginator
from account.authorization import TokenAuthentication
from movies.models import Movie
from movies.schemas.movies import MovieOut
from utils.schemas import MessageOut


User = get_user_model()

movies_controller = Router(tags=['Movies'])

@movies_controller.get('{page}', response={200: list[MovieOut], 404: MessageOut})
def list_movies(request,page_num: int ):
    movies = Movie.objects.prefetch_related('categories', 'movie_actors').all().order_by('title')
    paginator = Paginator(movies, 4)
    movies = paginator.get_page(page_num)
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

@movies_controller.post('/favorites/{id}',auth=TokenAuthentication(), response={201: MessageOut, 404: MessageOut})
def favorite_movie_add(request, id: UUID4):
    try:
        user=User.objects.get(id=requests.auth['id'])
        movie=Movie.objects.get(id=id)
        if Movie.objects.filter(id_user=user.id,id=id):
            return 201,{'msg': 'movies added to your favorites'}
        else:
            movie.user.add(user)
            return 201, {'msg': 'movies added to your favorites'}
    except:
        return 404, {'msg': 'movies is not added to your favorites'}

@movies_controller.delete('/favorites/{id}',auth=TokenAuthentication(), response={201: MessageOut, 404: MessageOut})
def favorite_movie_del(request, id: UUID4):
    try:
        user = User.objects.get(id=requests.auth['id'])
        movie = Movie.objects.get(id=id)
        if Movie.objects.filter(id_user=user.id, id=id):
            movie.user.remove(user)
            return 201, {'msg': 'movies deleted from your favorites'}
        else:
            return 404, {'msg': 'the movies not found your favorites'}
    except:
        return 404, {'msg': 'there is error in  your favorites'}

