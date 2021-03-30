from datetime import date

from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token


class MyUser(AbstractUser):
    cash = models.DecimalField(decimal_places=2, max_digits=15, default=10000)


class Hall(models.Model):
    GREEN = "Green"
    BLUE = "Blue"
    RED = "Red"
    HALL_CHOICES = [(GREEN, 'Green'), (BLUE, 'Blue'), (RED, 'Red')]
    hall = models.CharField(max_length=10, choices=HALL_CHOICES)
    places = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f'{self.hall} has {self.places} places'


def place_default():
    return Hall.places


class Seance(models.Model):
    title = models.CharField(max_length=20)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    ticket_value = models.DecimalField(decimal_places=2, max_digits=7)
    used = models.IntegerField(default=0)
    seats = models.PositiveIntegerField(default=place_default)

    def __str__(self):
        return f'{self.title} going from {self.date_start} to {self.date_end} at {self.start} in {self.hall.hall}'

    def validate_seats(self, ticket_count):
        if self.seats >= ticket_count:
            return True
        return False

    # @property
    # def today(self):
    #     today = Seance.objects.get(date_start__lte=date.today(), date_end__gte=date.today())
    #     if today:
    #         return today
    #     return None


class Order(models.Model):
    customer = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    film = models.ForeignKey(Seance, on_delete=models.CASCADE)
    tickets = models.PositiveIntegerField(default=1)


class OurToken(Token):
    time_to_die = models.DateTimeField(null=True)
