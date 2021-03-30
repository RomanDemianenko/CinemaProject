from django import forms
from django.contrib import messages
from django.db.models import Q
from django.forms import ModelForm

from mysite.models import MyUser, Hall, Seance, Order


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ['username', 'password']


class RegistrationForm(forms.ModelForm):
    name = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        if MyUser.objects.filter(username=username).exists():
            raise forms.ValidationError(f'This {username} has already registration')
        return username

    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError('Inncorect password')
        return self.cleaned_data

    class Meta:
        model = MyUser
        fields = ['username', 'name', 'email', 'password', 'confirm_password']


class HallForm(ModelForm):
    class Meta:
        model = Hall
        fields = '__all__'


class SeanceForm(ModelForm):
    def clean(self):
        hall = self.cleaned_data.get('hall')
        time_start = self.cleaned_data.get('start')
        time_end = self.cleaned_data.get('end')
        day_start = self.cleaned_data.get('date_start')
        day_end = self.cleaned_data.get('date_end')
        if day_end <= day_start:
            raise forms.ValidationError("You should mix up date")
        if time_end <= time_start:
            raise forms.ValidationError("You should mix up time")
        q1 = Q(hall=hall.id, date_start__range=(day_start, day_end), start__range=(time_start, time_end))
        q2 = Q(hall=hall.id, date_start__range=(day_start, day_end), end__range=(time_start, time_end))
        q3 = Q(hall=hall.id, date_end__range=(day_start, day_end), start__range=(time_start, time_end))
        q4 = Q(hall=hall.id, date_end__range=(day_start, day_end), end__range=(time_start, time_end))
        if Seance.objects.filter(q1 | q2 | q3 | q4):
            raise forms.ValidationError('You must change hall/date/time')
        return self.cleaned_data

    class Meta:
        model = Seance
        fields = ['title', 'hall', 'date_start', 'date_end', 'start', 'end', 'ticket_value']


class SeanceUpdateForm(ModelForm):
    class Meta:
        model = Seance
        fields = ['id', 'title', 'hall', 'date_start', 'date_end', 'start', 'end', 'ticket_value']

    def clean(self):
        cleaned_data = super().clean()
        seance_id = self.instance.id
        hall = self.cleaned_data.get('hall')
        time_start = self.cleaned_data.get('start')
        time_end = self.cleaned_data.get('end')
        day_start = self.cleaned_data.get('date_start')
        day_end = self.cleaned_data.get('date_end')
        if day_end <= day_start:
            raise forms.ValidationError("You should mix up date")
        if time_end <= time_start:
            raise forms.ValidationError("You should mix up time")
        q1 = Q(hall=hall.id, date_start__range=(day_start, day_end), start__range=(time_start, time_end))
        q2 = Q(hall=hall.id, date_start__range=(day_start, day_end), end__range=(time_start, time_end))
        q3 = Q(hall=hall.id, date_end__range=(day_start, day_end), start__range=(time_start, time_end))
        q4 = Q(hall=hall.id, date_end__range=(day_start, day_end), end__range=(time_start, time_end))
        if Seance.objects.filter(q1 | q2 | q3 | q4).exclude(id=seance_id):
            raise forms.ValidationError('You must change hall/date/time')

        return self.cleaned_data


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def is_valid(self):
        user = self.data.get('customer')
        user_cash = user.cash
        film = self.data.get('film')
        tickets = self.data.get('tickets')
        if film.ticket_value * tickets > user_cash:
            raise forms.ValidationError('heyyyyy?')
        elif film.seats < tickets:
            raise forms.ValidationError('WE don`t have enough items')
        return self.data
