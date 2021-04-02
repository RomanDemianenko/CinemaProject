from datetime import datetime, date, timedelta

from django.contrib.auth import authenticate, logout
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework import exceptions, permissions
from django.db.models import Sum, Avg, Func, F, FloatField, Q
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication, BaseAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.views import APIView

from Cinema.settings import TIME_TO_DIE, AUTH_USER_MODEL, USED
from mysite.api.serializers import SeanceSerializer, OrderSerializer, HallSerializer, \
    RegisterSerializer, AuthUserSerializer, MyAuthTokenSerializer
from mysite.models import Seance, Order, MyUser, Hall, OurToken


class AuthViewSet(viewsets.ModelViewSet):
    """There I used decorate @action for registration and logout"""
    permission_classes = [AllowAny, ]
    serializer_class = RegisterSerializer

    @action(methods=['POST'], detail=False)
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['password'] != serializer.validated_data['confirm_password']:
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

        user = MyUser.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            cash=serializer.validated_data['cash'])
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=['POST', ], detail=False)
    def logout(self, request):
        logout(request)
        data = {'success': 'Sucessfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)


class AuthToken(ObtainAuthToken):
    """There I wrote create Token and his rewrite after N time"""
    serializer_class = MyAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = OurToken.objects.get_or_create(user=user)

            if token[0].time_to_die < timezone.now():
                token[0].delete()
                token = OurToken.objects.get_or_create(user=user)
                token[0].time_to_die = timezone.now() + TIME_TO_DIE
                token[0].save()

            return Response({'token': token[0].key, 'username': user.username, })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HallViewSet(viewsets.ModelViewSet):
    queryset = Hall.objects.all()
    serializer_class = HallSerializer

    def get_queryset(self):
        queryset = Hall.objects.all()
        value = self.request.query_params.get('name', None)
        if value is not None:
            queryset = queryset.filter(hall=value)
        return queryset


class SeanceViewSet(viewsets.ModelViewSet):
    """There I wrote create, update for seance. Also, I use decorate @action fro sort by value/seance start time/today seances
    / and tomorrow seances. And I used get_queryset for getting some filters
    """
    queryset = Seance.objects.all()
    serializer_class = SeanceSerializer

    def create(self, request, *args, **kwargs):
        serializer = SeanceSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            hall = Hall.objects.get(id=serializer.data.get('hall'))
            new_seance = Seance(
                title=data.get('title'), hall=hall, date_start=data.get('date_start'), date_end=data.get('date_end'),
                start=data.get('start'), end=data.get('end'), ticket_value=data.get('ticket_value'), used=USED,
                seats=hall.places)
            new_seance.save()
            return Response(serializer.errors, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        queryset = Seance.objects.all()
        hall_id = self.request.query_params.get('hall', None)
        time1 = self.request.query_params.get('time1', None)
        time2 = self.request.query_params.get('time2', None)

        if hall_id:
            hall = Hall.objects.get(id=hall_id)
            queryset = queryset.filter(hall=hall, date_start__lte=date.today(), date_end__gte=date.today())

        elif hall_id and time1 and time2:
            hall = Hall.objects.get(id=hall_id)
            queryset = queryset.filter(hall=hall, date_start__lte=date.today(), date_end__gte=date.today(),
                                       start__gte=time1, end__lte=time2)
        else:
            queryset = Seance.objects.all()

        return queryset

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        seance = get_object_or_404(Seance.objects.filter(id=pk))
        serializer = SeanceSerializer(instance=seance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.errors, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def value(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('ticket_value')
        serializer = SeanceSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False)
    def start(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('start')
        serializer = SeanceSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False)
    def today(self, request, *args, **kwargs):
        queryset = self.queryset.filter(date_start__lte=date.today(), date_end__gte=date.today())
        serializer = SeanceSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False)
    def tomorrow(self, request, *args, **kwargs):
        queryset = self.queryset.filter(date_start__lte=date.today() + timedelta(days=1),
                                        date_end__gte=date.today() + timedelta(days=1))
        serializer = SeanceSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    """
    There I wrote buying process and getting buying history
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            seance = Seance.objects.get(id=serializer.data.get('film'))
            customer = request.user
            new_order = Order.objects.create(
                customer=customer, film=seance, tickets=serializer.data.get('tickets'))
            seance.used += int(new_order.tickets)
            if seance.validate_seats(new_order.tickets):
                seance.seats -= int(new_order.tickets)
                customer.cash -= new_order.film.ticket_value * new_order.tickets
                seance.save()
                customer.save()
                return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(customer=user)
        return queryset


class Authentication(BaseAuthentication):
    def authenticate(self, request):
        username = request.META.get('HTTP_X_USERNAME')
        if not username:
            return None

        try:
            user = MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('Did not find this user')

        return (user, None)
