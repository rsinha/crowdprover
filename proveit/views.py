from django.template import Context, loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
import re
from django.core.validators import email_re

def index(request):
    context = Context({})
    return render(request,'main/newmainpage.html',context)

def loginpage(request):
	if request.user.is_authenticated(): # Just go back to the main page
		context = Context({})
		return render(request,'main/newmainpage.html',context)
	else: # Stay at login page, and let user fill details
		context = Context({})
		return render(request,'main/login.html',context)

def logging(request):
	if request.user.is_authenticated(): # Just go back to the main page. This is important if someone goes to url /submit
		context = Context({})
		return render(request,'main/newmainpage.html',context)

	# TODO: This check seems a little strange. Could there be faults?
	if not request.POST:
		context =  Context({})
		return render(request,'main/newmainpage.html',context)

	# Try to sign user in
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username,password=password)
	if user is not None:
		if user.is_active:
			login(request,user)
			context = Context({})
			return render(request,'main/newmainpage.html',context)
		else:
			return render(request,'main/login.html',{'error_message':"This account has been disabled"})
	else:
		return render(request,'main/login.html',{'error_message':"Incorrect username or password"})

def logoutuser(request):
	logout(request)
	context = Context({})
	return render(request,'main/newmainpage.html',context)

def registerpage(request):
	if request.user.is_authenticated(): # Just go back to the main page
		context = Context({})
		return render(request,'main/newmainpage.html',context)
	else:
		context = Context({})
		return render(request,'main/register.html',context)

def registering(request):
	if request.user.is_authenticated(): # Just go back to the main page. This is important if someone goes to url /regsubmit
		context = Context({})
		return render(request,'main/newmainpage.html',context)

	# TODO: This check for non-emptiness of the POST request seems strange to me. Could there be a better way?
	# TODO: Use Django forms for the register form validation

	if not request.POST:
		context =  Context({})
		return render(request,'main/newmainpage.html',context)

	firstname = request.POST['firstname']
	lastname = request.POST['lastname']
	email = request.POST['email']
	username = request.POST['username']
	password = request.POST['password']

	name_re = re.compile("^[a-zA-Z]+$")
	username_re = re.compile("^[a-zA-Z0-9]+[\w]*$")

	firstname_error = ""
	lastname_error = ""
	email_error = ""
	username_error = ""
	password_error = ""

	form_valid = 1

	if firstname=="" or firstname is None:
		firstname_error="First name is compulsory"
		form_valid = 0
	elif not name_re.match(firstname):
		firstname_error="Invalid first name"
		form_valid = 0
	else:
		firstname_error=""

	if lastname=="" or lastname is None:
		lastname_error=""
	elif not name_re.match(lastname):
		lastname_error="Invalid last name"
		form_valid = 0
	else:
		lastname_error=""

	if email=="" or email is None:
		email_error="Email is compulsory"
		form_valid = 0
	elif not email_re.match(email):
		email_error="Invalid email address"
		form_valid = 0
	else:
		email_error=""

	if username=="" or username is None:
		username_error="Username is compulsory"
		form_valid = 0
	elif not username_re.match(username):
		username_error="Invalid username"
		form_valid = 0
	elif User.objects.filter(username=username).count():
		username_error="This username is already taken"
		form_valid = 0
	else:
		username_error=""

	if password=="" or password is None:
		password_error="Password is compulsory"
		form_valid = 0
	else:
		password_error=""

	if form_valid == 0:
		context = Context({'firstname_error':firstname_error,'lastname_error':lastname_error,'email_error':email_error,'username_error':username_error,'password_error':password_error})
		return render(request,'main/register.html',context)
	else: # Register user, log in, and return to main page
		u = User(username=username,first_name=firstname,last_name=lastname,email=email)
		u.save()
		u.set_password(password)
		u.save()
		v = authenticate(username=username,password=password)
		login(request,v)
		context = Context({})
		return render(request,'main/newmainpage.html',context)





