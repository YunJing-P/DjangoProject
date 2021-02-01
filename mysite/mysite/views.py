from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hi man, this is the main page")
