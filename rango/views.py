# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def index(request):
    request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages':pages_list}
#    context_dict = {'boldmessage':"Crunchy, creamy, cookie, candy, cupcake!"}
    #20.1.2018-start playing around with templates
    #1.2.2018-response pattern used for cookies
        # This function alters the response object by setting/updating cookies
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context=context_dict)
    #return HttpResponse("Rango says ayyy<br><a href=\"/rango/about\">link</a>")
    return response



# A helper method for storing cookie information serverside
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

#1.2.2018 second cookie handler helper function
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    if(datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits



"""
# A cookie handling helper function (ch.10)
# implementing a 'visits counter'
def visitor_cookie_handler(request, response):
    # Get the number of visits, using COOKIES.get() to obtain the visits cookie
    # If the cookie exists, the value returned is casted to an integer
    # If the cookie doesn't exist, then the default value of 1 is used
    visits = int(request.COOKIES.get('visits', '1'))
    last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    # If it's been more than a day since the last visit
    #                                     temporarily set to 'seconds' rather than 'days'
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        # update last_visit cookie
        response.set_cookie('last_visit', str(datetime.now()))
    else:
        visits = 1
        # set last visit cookie
        response.set_cookie('last_visit', last_visit_cookie)
    # Update/set the visits cookie
    response.set_cookie('visits', visits)
"""
def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    context_dict = {'boldmessage':"\"Here\'s the about page!\""}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/about.html', context=context_dict)
    #return HttpResponse("Rango says ayyy<br><a href=\"/rango/about\">link</a>")
    return response

def show_category(request, category_name_slug):
    context_dict = {}
    try:
        # can we find a category name slug matching?
        # get() raises DoesNotExist exception if not
        # get() returns one model instance or raises exception
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    #this view function can handle three scenarios: 1-show a new, blank form for adding a category
    #2-save form data provided by the user (and it's good) and rendering the rango index page
    #3-if there are errors in the form data, redisplay the form with error messages

    #here it gets cool
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            #new category has been saved, and we could give a confirmation message here
            #but since the most rect category added is on the index page
            #we can just redirect the user back to the index page
            return index(request)
        else:
            #the form supplied contained errors, just print them to the terminal
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method== 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context_dict = {'form':form, 'category':category}
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    # a boolean to keep track of whether or not registration worked
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        #if the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            #hash the password with set_password method
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            #invalid form or forms
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances
        # These forms will be blank, ready for user input
        user_form = UserForm()
        profile_form = UserProfileForm()
    context = {'user_form':user_form, 'profile_form': profile_form, 'registered': registered}
    return render(request, 'rango/register.html', context)

def user_login(request):
    if request.method == 'POST':
        # use request.Post.get('<variable>') instead of request.POST['<variable>'] because the first returns
        # None if the value doesn't exist, and the latter method returns a KeyError exception in the same situation
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            # is the account enabled or disabled?
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # account is inactive, so no logging in for youu
                return HttpResponse("Your Rango account is disabled")
        else:
            # Bad login details were provided
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    # request is not a HTTP POST so display the login form
    # this scenario will most likely be a HTTP GET
    else:
        #No context variables hence the empty dictionary
        return render(request, 'rango/login.html', {})

@login_required
def user_logout(request):
    #As this function is being executed given the login_required decorator, we can just go ahead and logout
    logout(request)
    return HttpResponseRedirect(reverse('index'))







