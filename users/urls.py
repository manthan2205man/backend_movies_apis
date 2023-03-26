from django.urls import path
from .views import *


urlpatterns = [

    # Auth APIS
    path('register/', UserRegisterView.as_view()),
    path('logout/', UserLogoutView.as_view()),

    # movies api 
    path('movies/', ListMoviesView.as_view()),

    # collections api 
    path('collection/', CreateListCollectionsView.as_view()),
    path('collection/<str:id>/', DetailUpdateDeleteCollectionsView.as_view()),

    # request-count api 
    path('request-count/', GetRequestCountView.as_view()),
    path('request-count/reset/', ResetRequestCountView.as_view()),

]