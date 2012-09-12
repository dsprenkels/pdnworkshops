import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
# from django.contrib import messages

from pdn.workshops.models import Workshop, User, WorkshopRating

# Create your views here.
def inschrijven(request):
	workshops = list(Workshop.objects.all())
	if request.method == 'POST':
		user = User()
		user.naam = request.POST['naam']
		user.email = request.POST['email']
		user.save()
		for ws in workshops:
			rating = WorkshopRating()
			rating.workshop = ws
			rating.user = user
			rating.rating = request.POST['workshop_%s' % ws.id]
			rating.save()
		return render_to_response('complete.html', {}, context_instance=RequestContext(request))
	return render_to_response('inschrijven.html', {'workshops': workshops}, context_instance=RequestContext(request))
