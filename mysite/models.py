from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token


class MyUser(AbstractUser):
    cash = models.DecimalField(decimal_places=2, max_digits=15, default=10000)


# class Places(models.Model):
#     places = models.PositiveIntegerField(default=10)
#
#     class Meta:
#         abstract = True
#         ordering = ['places']


class Hall(models.Model):
    GREEN = "Green"
    BLUE = "Blue"
    RED = "Red"
    HALL_CHOICES = [(GREEN, 'Green'), (BLUE, 'Blue'), (RED, 'Red')]
    hall = models.CharField(max_length=10, choices=HALL_CHOICES)
    places = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f'{self.hall} has {self.places} places'

    # class Meta(Places.Meta):
    #     pass


def place_default():
    return Hall.places


class Seance(models.Model):
    title = models.CharField(max_length=20)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    ticket_value = models.DecimalField(decimal_places=2, max_digits=7)
    used = models.IntegerField(default=0)
    seats = models.PositiveIntegerField(default=place_default)

    def __str__(self):
        return f'{self.title} going from {self.start} to {self.end}'

    # class Meta(Hall.Meta):
    #     pass


class Order(models.Model):
    customer = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    film = models.ForeignKey(Seance, on_delete=models.CASCADE)
    tickets = models.PositiveIntegerField(default=1)
# class OurToken(Token):
#     time_to_die = models.DateTimeField(null=True)
