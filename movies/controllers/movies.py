from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from movies.schemas.favorite import FavoriteOut
from ninja import Router
from pydantic.types import UUID4
from ninja.pagination import paginate, PageNumberPagination

from account.authorization import TokenAuthentication
from movies.models import Movie
from movies.schemas.movies import MovieOut
from utils.schemas import MessageOut

User = get_user_model()
movies_controller = Router(tags=['Movies'])




@movies_controller.get('', response={200: list[MovieOut], 404: MessageOut})
def list_movies(request):
    movies = Movie.objects.prefetch_related('categories', 'movie_actors').all()
    if movies:
        return 200, movies
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

#add movie that from their favorite list

@movies_controller.post('/movies/favorites/{id}', auth=TokenAuthentication(), response={200: MessageOut, 404: MessageOut})
def favorite_Add_movies(request,id: UUID4):
    user = User.objects.get(id=request.auth['id'])
    movie=Movie.objects.get(id=id)
    if Movie.objects.filter(user__id=user.id, id=id):

        return 200, {'msg': 'movie already add'}
    else:
        movie.user.add(user)
        return 200, {'msg': 'movie add successfully'}

#remove movie that from their favorite list
@movies_controller.delete('/movies/favorites/{id}', auth=TokenAuthentication(), response={200: MessageOut, 404: MessageOut})
def favorite_delet_movies(request,id: UUID4):
    user = User.objects.get(id=request.auth['id'])
    movie=Movie.objects.get(id=id)
    if Movie.objects.filter(user__id=user.id, id=id):
        movie.user.remove(user)
        return 200, {'msg': 'movie deleted successfully'}
    else:
        movie.user.remove(user)
        return 200, {'msg': 'movie already deleted'}

#listing movies
@movies_controller.get('/', response=list[MovieOut])
@paginate(PageNumberPagination,page_size=4)
def listing_series(request):
    return Movie.objects.all()








@movies_controller.get('/{id}', response={200: MovieOut, 404: MessageOut})
def get_movie(request, id: UUID4):
    try:
        movie = Movie.objects.get(id=id)
        return 200, movie
    except Movie.DoesNotExist:
        return 404, {'msg': 'There is no movie with that id.'}


# ()

