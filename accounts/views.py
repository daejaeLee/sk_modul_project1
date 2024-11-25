from django.shortcuts import render, redirect
from .models import CustomUser
from django.db import connection
#from django.contrib.auth import authenticate

def register(request):
    url = 'board:board_home'
    if request.method == "POST":
        email = request.POST['email']
        name = request.POST['name']
        password1 = request.POST['password1']
        user = CustomUser.objects.filter(email = email)
        print(len(user))
        if len(user) == 0:
            CustomUser.objects.create_user(
                username=email,
                email=email,  
                name=name,  
                password=password1
            )            
        else:
            alert = {'msg':'중복된 아이디 입니다.', 'url':'register'}
            return render(request, 'alert.html', alert)    

        print(url)
        return redirect(url)
    else:        
        return render(request, 'accounts/register.html')
    
def login(request):
    url = 'board:board_home'
    alert = ""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)
        user = CustomUser.objects.filter(email = email)
        if email is not None and password is not None and len(user) != 0:
            #user = authenticate(request, username=email, password=password)
            #print(user, type(user))
            #auth_login(request, user)
            pwd = user.first().password
            print(pwd)
            if pwd == password:
                request.session['user'] = email 
                print('seesion : ', request.session.get('user'))
            else:
                alert = {'msg':'이메일 또는 비밀번호가 잘못되었습니다.', 'url':'login'}
        else:
            alert = {'msg':'이메일 또는 비밀번호가 잘못되었습니다.', 'url':'login'}
        print(alert)
        if alert != "": return render(request, 'alert.html', alert)
        return redirect(url)
    else:
        return render(request, 'accounts/login.html')


def logout(request):
    if request.session.get('user'):
        del(request.session['user'])
    print(request.session.keys())
        
    return redirect('board:board_home')