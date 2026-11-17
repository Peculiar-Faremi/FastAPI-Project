from redis import Redis
from app.config import settings

r=Redis.from_url(settings.REDIS_URL, decode_responses=True) 