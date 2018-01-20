# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says ayyy<br><a href=\"/rango/about\">link</a>")

def about(request):
    return HttpResponse("Rango says \"here is the about page\"<br><a href=\"/rango\">link</a>")

