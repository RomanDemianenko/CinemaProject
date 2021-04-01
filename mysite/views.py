from django.shortcuts import render
from django import template
from django.utils.timezone import utc
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, RedirectView
from django.views.generic.base import View
from datetime import datetime, timedelta, date, time
from django.utils import timezone
from django.db.models import Sum, Avg, Func, F, FloatField, Q
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django_filters.views import FilterView

from mysite.forms import RegistrationForm, LoginForm, HallForm, SeanceForm, OrderForm, SeanceUpdateForm
from mysite.models import MyUser, Seance, Hall, Order


class UserLoginView(LoginView):

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm(request.POST)
        context = {'form': form}
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'You are login')
                    return HttpResponseRedirect('/cinema/')

        else:
            messages.warning(request, 'Your login or password not correct')
            return HttpResponseRedirect('/cinema/')

        context = {'form': form}
        return render(request, 'login.html', context)


class RegistrationView(CreateView):
    model = MyUser

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        films = Seance.objects.all()
        context = {'form': form, 'product': films}
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.name = form.cleaned_data['name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            messages.success(request, 'Welcome in our club')
            return HttpResponseRedirect('/cinema/')
        context = {'form': form}
        return render(request, 'registration.html', context)


class UserLogout(LogoutView):
    template_name = 'log_out.html'
    next_page = '/cinema/'


class SeanceListView(ListView, FilterView):
    model = Seance
    form = SeanceForm
    ordering = ['-id']
    paginate_by = 10
    template_name = 'cinema.html'

    def get_ordering(self):
        ordering = self.request.GET.get('orderby')
        return ordering

    def get_queryset(self):
        ordering = self.request.GET.get('orderby')
        if ordering == 'today':
            queryset = Seance.objects.filter(date_start__lte=date.today(), date_end__gte=date.today()).order_by('start')
        else:
            queryset = Seance.objects.all()
        return queryset


class HallCreatView(PermissionRequiredMixin, CreateView):
    permission_required = 'request.user.is_superuser'
    model = Hall
    form_class = HallForm
    success_url = '/cinema/'
    template_name = 'create.html'


class SeanceUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'request.user.is_superuser'
    model = Seance
    form_class = SeanceUpdateForm
    template_name = 'update.html'
    success_url = '/cinema/'

    def post(self, request, *args, **kwargs):
        seance_pk = self.kwargs['pk']
        seance = Seance.objects.get(id=seance_pk)
        form = SeanceUpdateForm(request.POST, instance=seance)
        if form.is_valid():
            seance = form.save(commit=False)
            seance.seats = seance.hall.places
            seance.save()
            messages.success(self.request, "You Update the seance")
            return HttpResponseRedirect('/cinema/')
        else:
            messages.warning(self.request, 'You must change hall/date/time')
        context = {'form': form}
        return render(request, 'update.html', context)


class SeanceCreatView(PermissionRequiredMixin, CreateView):
    permission_required = 'request.user.is_superuser'
    model = Seance
    form_class = SeanceForm
    success_url = '/cinema/'
    template_name = 'create.html'

    def post(self, request, *args, **kwargs):
        form = SeanceForm(request.POST)
        if form.is_valid():
            seance = form.save(commit=False)
            seance.seats = seance.hall.places
            seance.save()
            messages.success(self.request, "You create the new seance")
            return HttpResponseRedirect('/cinema/')
        else:
            messages.warning(self.request, 'You must change hall/date/time')
        context = {'form': form}
        return render(request, 'create.html', context)


class SeanceTodayListView(ListView):
    model = Seance
    form = SeanceForm
    paginate_by = 5
    ordering = ['date_start']
    template_name = 'today.html'

    def get_queryset(self):
        queryset = Seance.objects.filter(date_start__lte=date.today(), date_end__gte=date.today())
        return queryset


class SeanceTomorrowListView(ListView):
    model = Seance
    form = SeanceForm
    paginate_by = 5
    ordering = ['date_start']
    template_name = 'tomorrow.html'

    def get_queryset(self):
        q1 = Q(date_start__lte=date.today() + timedelta(days=1))
        q2 = Q(date_end__gte=date.today() + timedelta(days=1))
        queryset = Seance.objects.filter(q1 & q2)
        return queryset


class BuyingCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    model = Order
    form_class = OrderForm
    success_url = '/cinema/'

    def post(self, request, *args, **kwargs):

        user_quantity = request.POST['tickets']
        user_quantity = int(user_quantity)
        seance_id = request.POST['seance']
        seance = Seance.objects.get(id=seance_id)
        user_id = request.POST['customer']
        user = MyUser.objects.get(id=user_id)
        if seance.seats >= user_quantity:
            if user.cash >= user_quantity * seance.ticket_value:
                user.cash -= user_quantity * seance.ticket_value
                order = Order.objects.create(customer=user, film=seance, tickets=user_quantity)
                seance.used += user_quantity
                seance.seats -= user_quantity
                user.save()
                seance.save()
                order.save()
                messages.success(self.request, 'Enjoy the Movie')
            else:
                messages.warning(self.request, 'You need to fill up a wallet')
        else:
            messages.warning(self.request, 'We don`t have enough staff')
        return HttpResponseRedirect('/cinema/')


class OrdersListView(LoginRequiredMixin, ListView):
    model = Order
    form = OrderForm
    paginate_by = 5
    login_url = '/login/'
    ordering = ['-date_start']
    template_name = 'my_orders.html'

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(customer=user)
        return queryset

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(OrdersListView, self).get_context_data(**kwargs)
        context['total_prices'] = Order.objects.filter(customer=user).aggregate(
            avg=Sum(F('film__ticket_value') * F('tickets'), output_field=FloatField())).get('avg')
        return context
