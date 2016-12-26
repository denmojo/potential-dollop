from pyramid.view import view_config
import transaction
import pyramid.httpexceptions as exc
from services.record import RecordService
from datetime import datetime
from formencode import Schema, validators
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from quippy_wat.models import DBSession, Quip

class QuipSchema(Schema):
    submitter = validators.UnicodeString()
    quipped_text = validators.UnicodeString()
    source = validators.UnicodeString()
    source_date = validators.DateConverter(month_style='mm/dd/yyyy', not_empty=True)

@view_config(route_name='my_view', renderer='templates/index.pt')
def my_view(request):
    return {'project': 'quippy_wat'}

@view_config(route_name='home',
             renderer='templates/index.pt')
def home(request):
    page = int(request.params.get('page', 1))
    paginator = RecordService.get_paginator(request, page)
#    quips = DBSession.query(Quip).order_by(Quip.created_date.desc()).all()
    form = Form(request, schema=QuipSchema())
    return {'paginator': paginator, 'page':page, 'form': FormRenderer(form)}


@view_config(route_name='newquip',
             renderer='templates/index.pt',
             request_method='POST')
def newquip(request):
    form = Form(request, schema=QuipSchema())
    if not form.validate:
        raise exc.HTTPBadRequest
        
    sdstr = request.POST.get('source_date')
    source_d = datetime.strptime(sdstr, '%m/%d/%Y')

    q = Quip(
        quipped_text=request.POST.get('quipped_text', 'nobody'),
        submitter=request.POST.get('submitter', 'nobody'),
        source_date=source_d,
        source=request.POST.get('source', 'nothing'),
    )

    with transaction.manager:
        DBSession.add(q)

    raise exc.HTTPSeeOther('/quips')

@view_config(route_name='sorted',
             renderer='templates/sorted.pt')
def sorted(request):
    key = request.params['q']
    if key == 'oldest':
        quips = DBSession.query(Quip).order_by(Quip.source_date.asc()).all()
    else:
        quips = DBSession.query(Quip).order_by(Quip.source_date.desc()).all()
    return{'quips': quips}
    
@view_config(route_name='quip_autocomplete',
             renderer='json')
def quip_autocomplete(request):
    if 'query' not in request.params:
        abort(400)
    fragment = request.params['query']
    keywords = fragment.split()
    searchstring = "%%".join(keywords)
    searchstring = '%%%s%%' %(searchstring)
    try:
        ac_q = DBSession.query(Quip)
        res = ac_q.filter(Quip.quipped_text.ilike(searchstring)).limit(10)
        return dict(query=fragment,
                suggestions=[r.quipped_text for r in res],
                data=["%s" %(r.quipped_text) for r in res])
    except NoResultFound:
        return dict(query=fragment, suggestions=[], data=[])

