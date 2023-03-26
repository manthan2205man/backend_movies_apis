from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# Common Information Model 
class CommonInfo(models.Model):

    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        abstract=True


# User Model
class User(AbstractUser, CommonInfo):

    def __str__(self):
        return str(self.username) + ' - id - ' + str(self.id)
    
    class Meta:
        db_table = "users"


# User token Model
class UserToken(CommonInfo):
    
    user = models.ForeignKey(User, related_name="user_token", on_delete=models.CASCADE, null= True, blank=True)
    token = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.user) + ' UserTokenID ' + str(self.id)
    
    class Meta:
        db_table = "usertokens"


# Movie Model
class Movie(CommonInfo):
    
    title = models.CharField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True, blank=True)
    genres = models.CharField(null=True, blank=True, max_length=200)
    uuid = models.CharField(null=True, blank=True, max_length=100)

    def __str__(self):
        return str(self.title) + ' - id - ' + str(self.id)
    
    class Meta:
        db_table = "movies"


# Collection Model
class Collection(CommonInfo):
    
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    user = models.ForeignKey(User, related_name="collections", on_delete=models.CASCADE, 
                                                            null= True, blank=True)
    title = models.CharField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True, blank=True)
    movies = models.ManyToManyField(Movie, related_name='movies_collections', blank=True)

    def __str__(self):
        return str(self.title) + ' - id - ' + str(self.id)
    
    class Meta:
        db_table = "collections"


# Request Count Model
class RequestCount(CommonInfo):

    count = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return str(self.count) + ' - id - ' + str(self.id)
    
    class Meta:
        db_table = "request_counts"


