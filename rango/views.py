# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    context_dict = {'boldmessage':"Crunchy, creamy, cookie, candy, cupcake!"}
    #20.1.2018-start playing around with templates
    return render(request, 'rango/index.html', context=context_dict)
    #return HttpResponse("Rango says ayyy<br><a href=\"/rango/about\">link</a>")

def about(request):
    context_dict = {'boldmessage':"\"Here\'s the about page!\""}
    return render(request, 'rango/about.html', context=context_dict)

