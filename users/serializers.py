from rest_framework.serializers import ModelSerializer, Serializer
from . models import *
from rest_framework import serializers


# User Serializer
class UserSerializer(ModelSerializer):

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']


# Movie Serializer
class MovieSerializer(ModelSerializer):

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'genres', 'uuid']


# Collection Serializer
class InputCollectionSerializer(ModelSerializer):

    class Meta:
        model = Collection
        fields = ['id', 'title', 'description']


class CollectionSerializer(ModelSerializer):

    movies = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ['id', 'title', 'description', 'movies']

    def get_movies(self, obj):
        movies = obj.movies.filter(is_delete=False)
        if movies:
            serializer = MovieSerializer(movies, many=True)
            return serializer.data
        else:
            return []

