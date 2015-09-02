from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form) :

    username = forms.CharField(label='UserName', widget=forms.TextInput(attrs={'size' : '40'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

class ChangePasswd(forms.Form) :

    old_passwd = forms.CharField(label='Old Password', widget=forms.PasswordInput())
    passwd1 = forms.CharField(label='New Password', widget=forms.PasswordInput())
    passwd2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput())

    def verificate_password(self, username, old, new1, new2):

        user = User.objects.get(username=username)
        answer = {}
        if user.check_password(old) :
            if new1 == new2 :
                if len(new1) > 8:
                    user.set_password(new1)
                    user.save()
                    answer['success'] = True

                    return answer
                else:
                    answer['error'] = 'Your password is too small, at least 8 signs'
                    return answer
            else:
                answer['error'] = 'The passwords are not identical'
                return answer
        else:
            answer['error'] = 'Old password is invalid'
            return answer