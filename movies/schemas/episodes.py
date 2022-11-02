import datetime

from ninja import Schema
from pydantic.types import UUID4, Decimal, Optional

from movies.schemas.Actor import ActorOut


class EpisodeOut(Schema):
    id: UUID4
    title: str
    description: str
    trailer_url:  str = Optional
    release_date: datetime.date
    rating: Decimal
    actors: list[ActorOut] = Optional 
    image: str
