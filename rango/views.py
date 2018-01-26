# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages':pages_list}
#    context_dict = {'boldmessage':"Crunchy, creamy, cookie, candy, cupcake!"}
    #20.1.2018-start playing around with templates
    return render(request, 'rango/index.html', context=context_dict)
    #return HttpResponse("Rango says ayyy<br><a href=\"/rango/about\">link</a>")

def about(request):
    context_dict = {'boldmessage':"\"Here\'s the about page!\""}
    return render(request, 'rango/about.html', context=context_dict)

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

















