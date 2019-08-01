from django.shortcuts import render
from django.http import HttpResponse

from NLIDB import parsing


# Create your views here.
def index(request):
    #return HttpResponse("Test")
    #context = {}
    return HttpResponse(parsing.parse("Tunjukkan Dago Butik!"))
