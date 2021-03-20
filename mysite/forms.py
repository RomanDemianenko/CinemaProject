from django import forms
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
        # title = self.cleaned_data.get('title')
        # ticket_value = self.cleaned_data.get('ticket_value')
        hall = self.cleaned_data.get('hall')
        # hall_create = Hall.objects.get(id=hall_id)
        time_start = self.cleaned_data.get('start')
        time_end = self.cleaned_data.get('end')
        day_create = self.cleaned_data.get('date')
        if time_end <= time_start:
            raise forms.ValidationError("You mix up time")
        if Seance.objects.filter(hall=hall.id, date=day_create,
                                 start__range=(time_start, time_end)) or Seance.objects.filter(hall=hall.id,
                                                                                               date=day_create,
                                                                                               end__range=(
                                                                                                       time_start,
                                                                                                       time_end)):
            raise forms.ValidationError('You must change hall/date/time')
        return self.cleaned_data

    class Meta:
        model = Seance
        fields = ['title', 'hall', 'date', 'start', 'end', 'ticket_value']


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
