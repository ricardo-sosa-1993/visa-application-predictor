from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from . import config
import json

# Create your views here.

class Predictor(APIView):
    """View to get the predicted result of a visa application"""

    def post(self, request):
        """Returns the predicted result of a visa application"""
        model = cache.get(config.model_cache_key)
        result = model.predict(request.data)
        return Response(result)

class Options(APIView):
    """View to get the options of the fields of a visa application"""

    def get(self, request, format=None):
        """Returns the options of the fields of a visa application"""
        model = cache.get(config.model_cache_key)
        return Response(json.dumps(model.columns))

class Accuracy(APIView):
    """View to get the accuracy of the model"""

    def get(self, request, format=None):
        """Returns the accuracy of the model"""
        model = cache.get(config.model_cache_key)
        return Response(model.accuracy)