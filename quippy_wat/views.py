from pyramid.view import view_config
import transaction
import pyramid.httpexceptions as exc
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
    quips = DBSession.query(Quip).order_by(Quip.created_date.desc()).all()
    form = Form(request, schema=QuipSchema())
    return {'quips': quips, 'form': FormRenderer(form)}


@view_config(route_name='newquip',
             renderer='templates/index.pt',
             request_method='POST')
def newlunch(request):
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

