from django.shortcuts import get_object_or_404, render_to_response, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext
from django.contrib.auth import logout, authenticate, login

def welcome(request):
	return render_to_response('welcome.html', context_instance=RequestContext(request)) 

def logout_user(request):
    logout(request)
    return redirect(reverse('welcome')) 
