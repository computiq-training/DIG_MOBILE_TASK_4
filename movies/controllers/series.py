from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic.types import UUID4

from account.authorization import TokenAuthentication
from movies.models import Serial, Season, Episode
from movies.schemas.episodes import EpisodeOut
from movies.schemas.seasons import SeasonOut
from movies.schemas.series import SerialOut, FullSerialOut
from utils.schemas import MessageOut
from ninja.pagination import paginate, PageNumberPagination

User = get_user_model()
series_controller = Router(tags=['Series'])



@series_controller.get('', response={200: list[SerialOut], 404: MessageOut})
def list_series(request):
    series = Serial.objects.prefetch_related('categories', 'serial_actors').all().order_by('title')
    if series:
        return 200, series
    return 404, {'msg': 'There are no series yet.'}


@series_controller.get('/featured', response={200: list[SerialOut], 404: MessageOut})
def featured_series(request):
    series = Serial.objects.filter(is_featured=True).order_by('-rating')
    if series:
        return 200, series
    return 404, {'msg': 'There are no featured series.'}


@series_controller.get('/favorites', auth=TokenAuthentication(), response={200: list[SerialOut], 404: MessageOut})
def favorite_series(request):
    series = Serial.objects.filter(user__exact=request.auth['id']).order_by('-rating')
    if series:
        return 200, series
    return 404, {'msg': 'There are no featured movies.'}


#add movie that from their favorite list
@series_controller.post('/series/favorites/{id}', auth=TokenAuthentication(), response={200: MessageOut, 404: MessageOut})
def favorite_Add_movies(request,id: UUID4):
    user = User.objects.get(id=request.auth['id'])
    serial=Serial.objects.get(id=id)
    if Serial.objects.filter(user__id=user.id, id=id):

        return 200, {'msg': 'serial already add'}
    else:
        serial.user.add(user)
        return 200, {'msg': 'serial add successfully'}


#remove movie that from their favorite list
@series_controller.delete('/series/favorites/{id}', auth=TokenAuthentication(), response={200: MessageOut, 404: MessageOut})
def favorite_delet_movies(request,id: UUID4):
    user = User.objects.get(id=request.auth['id'])
    serial=Serial.objects.get(id=id)
    if Serial.objects.filter(user__id=user.id, id=id):
        serial.user.remove(user)
        return 200, {'msg': 'serial deleted successfully'}
    else:
        serial.user.remove(user)
        return 200, {'msg': 'serial already deleted'}

#listing Serials
@series_controller.get('/', response=list[SerialOut])
@paginate(PageNumberPagination,page_size=4)
def listing_series(request):
    return Serial.objects.all()




@series_controller.get('/{id}', response={200: FullSerialOut, 404: MessageOut})
def get_serial(request, id: UUID4):
    try:
        serial = Serial.objects.get(id=id)
        return 200, serial
    except Serial.DoesNotExist:
        return 404, {'msg': 'There is no serial with that id.'}


@series_controller.get('/{id}/seasons', response={200: list[SeasonOut], 404: MessageOut})
def get_seasons(request, id: UUID4):
    try:
        serial = Serial.objects.get(id=id)
        seasons = serial.seasons.all().order_by('number')
        return 200, seasons
    except Serial.DoesNotExist:
        return 404, {'msg': 'There is no serial with that id.'}


@series_controller.get('/{serial_id}/seasons/{season_id}/episodes', response={200: list[EpisodeOut], 404: MessageOut})
def list_episodes(request, serial_id: UUID4, season_id: UUID4):
    try:
        season = Season.objects.get(id=season_id, serial__id=serial_id)
        episodes = season.episodes.all().order_by('number')
        print(episodes)
        return 200, episodes
    except Season.DoesNotExist:
        return 404, {'msg': 'There is no season that matches the criteria.'}


@series_controller.get('/{serial_id}/seasons/{season_id}/episodes/{episode_id}',
                       response={200: EpisodeOut, 404: MessageOut})
def get_episodes(request, serial_id: UUID4, season_id: UUID4, episode_id: UUID4):
    try:
        season = Season.objects.get(id=season_id, serial_id=serial_id)
        episode = season.episodes.get(id=episode_id)
        return 200, episode
    except Season.DoesNotExist:
        return 404, {'msg': 'There is no season with that id.'}
    except Episode.DoesNotExist:
        return 404, {'msg': 'There is no episode that matches the criteria.'}
