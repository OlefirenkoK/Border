from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render_to_response , redirect
from loginsys.forms import LoginForm, ChangePasswd

# Create your views here.

def login(request):

    args = {}
    args.update(csrf(request))
    args['form'] = LoginForm()
    if request.POST:

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            args['login_error'] = 'Wrong!!! Incorrect Username or Password!'
            return render_to_response('login.html', args)
    else:
        return render_to_response('login.html', args)

def logout(request):

    auth.logout(request)
    return redirect('/')

def change_passwd(request) :

    args = {}
    args.update(csrf(request))
    username = auth.get_user(request).username
    args['username'] = username
    args['form'] = ChangePasswd()
    if request.POST :
        passwd_form = ChangePasswd(request.POST)
        if passwd_form.is_valid():
            old = request.POST.get('old_passwd', None)
            new1 = request.POST.get('passwd1', None)
            new2 = request.POST.get('passwd2', None)
            change = passwd_form.verificate_password(username ,old, new1, new2)
            if 'success' in change :
                return redirect('/list/')
            elif 'error' in change :
                args['passwd_error'] = change['error']
                return render_to_response('change_passwd.html', args)
            else:
                args['passwd_error'] = 'Error in passwd_form.verificate_password'
                return render_to_response('change_passwd.html', args)
        else:
            print('invalid')
            args['passwd_error'] = 'Form is invalid'
            return render_to_response('change_passwd.html', args)
    else:
        return render_to_response('change_passwd.html', args)