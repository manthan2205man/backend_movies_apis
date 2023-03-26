from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
import jwt, json, requests, string, random
from .serializers import *
from .models import *
from .utils import *
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime, timedelta, timezone
from requests.auth import HTTPBasicAuth


# User Register View
class UserRegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "detail": serializer.errors,
                                  "data":{}},
                            status= status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = User.objects.filter(username=username, is_delete=False).first()
        
        if user:
            # password hash
            new_password = check_password(password, user.password)
            if new_password == False:
                return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                      "detail": "The password does not match, Please recheck.",
                                       "data":{}},
                                            status=status.HTTP_400_BAD_REQUEST)
            # password hash
        else:
            # password hash
            hash_password = make_password(password)
            serializer.validated_data['password'] = hash_password
            # password hash

            serializer.save()
            user = User.objects.get(username=username, is_delete=False)

        dt = datetime.now(tz=timezone.utc) + timedelta(days=100)           
        letters = string.ascii_letters
        random_string = ''.join(random.choice(letters) for i in range(15))
        payload = {'exp': dt ,'id': user.id, 'username': username, 'random_string': random_string}
        encoded_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        UserToken.objects.create(user=user, token=encoded_token)

        return Response(data={"status": status.HTTP_200_OK,
                                "detail": "User successfully register, Token Generated.",
                                "data": {'access_token': encoded_token}},
                        status= status.HTTP_200_OK)
    

# User logout View
class UserLogoutView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        token = Authenticate(self, request)
        try:
            user_token = UserToken.objects.get(user=request.user, token=token, is_delete=False)
            user_token.is_delete = True
            user_token.save()
        except:
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                    "detail": 'Already Logged Out.',
                                    "data":{}},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                                "detail": "User Logged Out.",
                                "data":{}},
                        status=status.HTTP_200_OK)


# List Movies View
class ListMoviesView(GenericAPIView):

    def get(self, request, *args, **kwargs):

        page = request.GET.get('page')

        basic = HTTPBasicAuth(str(settings.API_USERNAME), str(settings.API_PASSWORD))

        if not page:
            url = "https://demo.credy.in/api/v1/maya/movies/"
        else:
            url = f"https://demo.credy.in/api/v1/maya/movies/?page={page}"

        payload={}
        files={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload, files=files, auth=basic)
        response = json.loads(response.text)
        if response.get('is_success', None) == False:
            response = requests.request("GET", url, headers=headers, data=payload, files=files, auth=basic)
            response = json.loads(response.text)

        return Response(data={"status": status.HTTP_200_OK,
                                "detail": "Movies get successfully.",
                                "data":response},
                        status=status.HTTP_200_OK)



# Create & List Collections View
class CreateListCollectionsView(GenericAPIView):
    serializer_class = CollectionSerializer

    def post(self, request, *args, **kwargs):
        serializer = InputCollectionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "detail": serializer.errors,
                                  'data':{}},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.validated_data['user'] = request.user
        serializer.save()

        collection = Collection.objects.get(id=serializer.data['id'])

        movies = request.data.get('movies', [])
        if movies:
            collection.movies.clear()
            try:
                for movie in movies:
                    movies_obj = Movie.objects.filter(uuid=movie['uuid']).first()
                    if not movies_obj:
                        movies_obj = Movie.objects.create(**movie)
                    collection.movies.add(movies_obj)
            except:
                return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "detail": 'Please provide proper json of movies.',
                                  'data':{}},
                            status=status.HTTP_400_BAD_REQUEST)


        return Response(data={"status": status.HTTP_201_CREATED,
                                "detail": "Collection Created Successfully.",
                                "data": {"collection_uuid": collection.id}},
                        status=status.HTTP_201_CREATED)

    def get(self, request):

        collections = Collection.objects.filter(user=request.user ,is_delete=False).distinct()

        count = collections.count()

        serializer = InputCollectionSerializer(collections, many=True)

        movies_list =[]
        for collection in collections:
            for movie in collection.movies.filter(is_delete=False):
                if not movie.genres == '':
                    movies_list.extend(movie.genres.split(","))

        from collections import Counter
        from itertools import repeat, chain
        result = list(chain.from_iterable(repeat(i, c) for i, c in Counter(movies_list).most_common()))
        result = list(set(result))
        if len(result) > 3:
            result = result[:3]

        collection_data = {'count' : count,
                'collections' : serializer.data}
        return Response(data={"status": status.HTTP_200_OK,
                                "detail": "My Collections list.",
                                "is_success": True,
                                'data':collection_data,
                                'favourite_genres': result},
                        status=status.HTTP_200_OK)


# Detail Update Delete Collections View
class DetailUpdateDeleteCollectionsView(GenericAPIView):
    serializer_class = CollectionSerializer

    def delete(self,request, id):
        collection = Collection.objects.filter(id=id, is_delete=False).first()
        if not collection:
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "detail": 'Collection not found.',
                                  "data":{}},
                            status=status.HTTP_404_NOT_FOUND)

        collection.is_delete=True
        collection.save()

        return Response(data={"status": status.HTTP_204_NO_CONTENT,
                              "detail": 'Collection deleted successfully.',
                              "data":{}},
                        status=status.HTTP_200_OK)
                                           
    def get(self,request,id):
        collection = Collection.objects.filter(id=id, is_delete=False).first()
        if not collection:
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "detail": 'Collection not found.',
                                  "data":{}},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(collection)
        
        return Response(data={"status": status.HTTP_200_OK,
                                "detail": "Collection get Successfully.",
                                "data": serializer.data},
                        status=status.HTTP_200_OK)

    def put(self,request,id):
        collection = Collection.objects.filter(id=id, user=request.user, is_delete=False).first()
        if not collection:
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "detail": 'collection not found.',
                                  "data":{}},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = InputCollectionSerializer(collection, data=request.data)
        
        if not serializer.is_valid():
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "detail": serializer.errors,
                                  'data':{}},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        collection = Collection.objects.get(id=serializer.data['id'])

        movies = request.data.get('movies', [])
        if movies:
            collection.movies.clear()
            try:
                for movie in movies:
                    movies_obj = Movie.objects.filter(uuid=movie['uuid']).first()
                    if not movies_obj:
                        movies_obj = Movie.objects.create(**movie)
                    collection.movies.add(movies_obj)
            except:
                return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "detail": 'Please provide proper json of movies.',
                                  'data':{}},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(collection)

        return Response(data={"status": status.HTTP_200_OK,
                                "detail": "Collection Updated Successfully.",
                                "data": serializer.data},
                        status=status.HTTP_200_OK)



# Get Request Count View
class GetRequestCountView(GenericAPIView):

    def get(self,request):
        request_count = RequestCount.objects.filter(id=1).first()
        if not request_count:
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "detail": 'Request Count not found.',
                                  "data":{}},
                            status=status.HTTP_404_NOT_FOUND)

        return Response(data={"status": status.HTTP_200_OK,
                              "detail": 'Request Count get successfully.',
                              "data":{'requests':request_count.count}},
                        status=status.HTTP_200_OK)
    

# Reset Request Count View
class ResetRequestCountView(GenericAPIView):

    def post(self,request):
        request_count = RequestCount.objects.filter(id=1).first()
        if not request_count:
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "detail": 'Request Count not found.',
                                  "data":{}},
                            status=status.HTTP_404_NOT_FOUND)
        request_count.count = 0
        request_count.save()
        return Response(data={"status": status.HTTP_200_OK,
                              "detail": 'Request Count reset Successfully.',
                              "data":{}},
                        status=status.HTTP_200_OK)