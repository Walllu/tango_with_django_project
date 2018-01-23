# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page

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


