from datetime import datetime, date, timedelta
from django.utils import timezone
# from time import timezone
from rest_framework import exceptions, permissions
from django.db.models import Sum, Avg, Func, F, FloatField, Q
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication, BaseAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from Cinema.settings import TIME_TO_DIE
from mysite.api.serializers import SeanceSerializer, OrderSerializer, MyAuthTokenSerializer, HallSerializer, \
    SeanceUpdateSerializer
from mysite.models import Seance, OurToken, Order, MyUser, Hall


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
    queryset = Seance.objects.all().order_by('id')
    serializer_class = SeanceSerializer

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        seance = get_object_or_404(Seance.objects.filter(id=pk))
        serializer = SeanceSerializer(instance=seance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.errors, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = SeanceSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            # seance = Seance.objects.all()
            hall = Hall.objects.get(id=serializer.data.get('hall'))
            # seats = hall.places
            new_seance = Seance(
                title=data.get('title'), hall=hall, date_start=data.get('date_start'), date_end=data.get('date_end'),
                start=data.get('start'), end=data.get('end'), ticket_value=data.get('ticket_value'), used=0,
                seats=hall.places)
            new_seance.save()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        queryset = Seance.objects.all()
        hall_id = self.request.query_params.get('hall', None)
        # today = self.request.query_params.get('data_start', None)
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


class AuthToken(ObtainAuthToken):
    serializer_class = MyAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = OurToken.objects.get_or_create(user=user)
        token.time_to_die = timezone.now() + timedelta(minutes=TIME_TO_DIE)
        token.save()
        return Response({
            'token': token.key,
            'username': user.username,
        })


class OrderViewSet(viewsets.ModelViewSet):
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

    def update(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        seance_id = self.i

    # def get_context_data(self, **kwargs):
    #     user = self.request.user
    #     context = self.get_context_data(**kwargs)
    #     context['total_prices'] = Order.objects.filter(customer=user).aggregate(
    #         avg=Sum(F('film__ticket_value') * F('tickets'), output_field=FloatField())).get('avg')
    #     return context


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
