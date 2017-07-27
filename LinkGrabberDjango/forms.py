from crispy_forms import helper
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import User
from django import forms

from LinkGrabberDjango.models import FeatureRequest


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["username", "password"]




User = get_user_model()

class FeatureRequestForm(forms.ModelForm):
    class Meta:
        model = FeatureRequest
        fields = ["title", "body"]


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username =self.cleaned_data.get("username")
        password =self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Something went wrong, Try Again.")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect Password.")
            if not user.is_active:
                raise forms.ValidationError("Account Disabled.")
            return super(UserLoginForm, self).clean(*args, **kwargs)



# our new form
class ContactForm(forms.Form):
    content = forms.CharField(
        required=True,
        widget=forms.Textarea
    )