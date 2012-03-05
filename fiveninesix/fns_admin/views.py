from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext

from forms import MailOrganizersForm
from organize import mail
from lots.models import Lot

@permission_required('organize.email_organizers')
def mail_organizers(request):
    if request.method == 'POST':    
        form = MailOrganizersForm(request.POST)
        if form.is_valid():
            mail.mail_organizers(form.data['subject'], form.data['message'])
            return redirect('fns_admin.views.mail_organizers_done')
    else:
        form = MailOrganizersForm()

    return render_to_response('fns_admin/mail_organizers.html', {
        'form': form,
    }, context_instance=RequestContext(request))

@permission_required('organize.email_organizers')
def mail_organizers_done(request):
    return render_to_response('fns_admin/mail_organizers_done.html', {}, context_instance=RequestContext(request))

@permission_required('lots.add_review')
def review_lots(request):
    reviewable_lots = _get_reviewable_lots()
    count = reviewable_lots.count()
    if reviewable_lots.count() > 20:
        reviewable_lots = reviewable_lots[:20]
    return render_to_response('fns_admin/review_lots.html', {
       'lots': reviewable_lots,
        'count': count,
    }, context_instance=RequestContext(request))

@permission_required('lots.add_review')
def get_lots_to_review(request):
    start, count = int(request.GET.get('start', 5)), int(request.GET.get('count', 20))
    reviewable_lots = _get_reviewable_lots()[start:(start + count)]
    return render(request, 'fns_admin/review_lots_snippet.html', { 'lots': reviewable_lots })

def _get_reviewable_lots():
    reviewless = Lot.objects.filter(is_vacant=True, owner__type__name__iexact='city', review=None)
    inaccessible = Lot.objects.filter(is_vacant=True, review__accessible=False)
    return reviewless | inaccessible
