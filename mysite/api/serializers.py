from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timezone, timedelta
from rest_framework import serializers

from Cinema.settings import TIME_TO_DIE
from mysite.models import MyUser, Order, Seance, Hall, OurToken


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = MyUser
        fields = ('id', 'username', 'email', 'password', 'cash', 'confirm_password')


class EmptySerializer(serializers.Serializer):
    pass


class AuthUserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ('id', 'username', 'email', 'password', 'cash', 'auth_token')
        read_only_fields = ('id', 'email', 'cash')

    def get_auth_token(self, obj):
        token = OurToken.objects.create(user=obj)
        return token.key


class MyAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label="Username", required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)

            if not user:
                error = ("We didn`t have this user in our system")
                raise serializers.ValidationError(error)

        else:
            error = ("You should fill fields")
            raise serializers.ValidationError(error)
        attrs['user'] = user

        return attrs


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username', 'email', 'password', 'cash']

        def create(self, validated_data):
            customer = MyUser(email=validated_data['email'],
                              username=['username']
                              )
            customer.set_password(validated_data['password'])
            customer.save()
            return customer


class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = ['id', 'hall', 'places']

        # read_only_fields = ['id']

    def create(self, validated_data):
        hall = Hall.objects.create(**validated_data)
        return hall


def place_default():
    return Hall.places


class SeanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seance

        fields = ['id', 'title', 'hall', 'date_start', 'date_end', 'start', 'end', 'ticket_value', 'used', 'seats']

    def validate(self, data):
        hall = data['hall']
        time_start = data['start']
        time_end = data['end']
        day_start = data['date_start']
        day_end = data['date_end']
        used = data['used']
        seats = data['seats']
        if seats != hall.places:
            raise serializers.ValidationError("Wrong seats, seats must equal ", hall.places)
        if used != 0:
            raise serializers.ValidationError("Used must equal 0!!!")
        if day_end <= day_start:
            raise serializers.ValidationError("You should mix up date")
        if time_end <= time_start:
            raise serializers.ValidationError("You should mix up time")
        q1 = Q(hall=hall, date_start__range=(day_start, day_end), start__range=(time_start, time_end))
        q2 = Q(hall=hall, date_start__range=(day_start, day_end), end__range=(time_start, time_end))
        q3 = Q(hall=hall, date_end__range=(day_start, day_end), start__range=(time_start, time_end))
        q4 = Q(hall=hall, date_end__range=(day_start, day_end), end__range=(time_start, time_end))
        if Seance.objects.filter(q1 | q2 | q3 | q4):
            raise serializers.ValidationError('You must change hall/date/time')
        return data


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer', 'film', 'tickets']

    def validate(self, data):
        user_cash = data['customer'].cash
        if data['film'].ticket_value * data['tickets'] > user_cash:
            raise serializers.ValidationError('heyyyyy?')
        elif data['film'].seats < data['tickets']:
            raise serializers.ValidationError('WE don`t have enough items')
        return data
