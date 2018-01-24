from django.core.cache import cache
from . import config
from .visa_model import VisaModel

model = cache.get(config.model_cache_key) # get model from cache
if model is None:
    cache.set(config.model_cache_key, VisaModel(), None) # save in the cache