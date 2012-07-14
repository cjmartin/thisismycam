from django.conf import settings
from django.shortcuts import render_to_response, redirect, get_object_or_404

def index(request):
    return render_to_response('cameras/index.html')