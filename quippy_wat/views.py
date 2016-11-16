from pyramid.view import view_config
import transaction
import pyramid.httpexceptions as exc
from datetime import datetime
from formencode import Schema, validators
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
    )

from pyramid.view import (
    view_config,
    view_defaults
    )

from .security import (
    USERS,
    check_password,
    hash_password
)

from quippy_wat.models import DBSession, Quip, User

class QuipSchema(Schema):
    submitter = validators.UnicodeString()
    quipped_text = validators.UnicodeString()
    source = validators.UnicodeString()
    source_date = validators.DateConverter(month_style='mm/dd/yyyy', not_empty=True)

@view_config(route_name='create_account', renderer='templates/create_account.pt')
def create_account(request):
    logged_in = request.authenticated_userid
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        u = User(
            login=login,
            password=hash_password(password),
        )

        with transaction.manager:
            DBSession.add(u)
        
        raise exc.HTTPSeeOther('/quips')
    
    return {}

@view_config(route_name='login', renderer='templates/login.pt')
def login(request):
    logged_in = request.authenticated_userid
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/quips'  # never use login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if check_password(password, DBSession.query(User).filter(User.login == login).first().password):
        #if check_password(password, USERS.get(login)):
            headers = remember(request, login)
            return HTTPFound(location=came_from,
                             headers=headers)
        message = 'Failed login'

    return dict(
        name='Login',
        message=message,
        url=request.application_url + '/quips/login',
        came_from=came_from,
        login=login,
        password=password
    )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    url = request.route_url('home')
    return HTTPFound(location=url,
                     headers=headers)
                         
@view_config(route_name='my_view', renderer='templates/index.pt')
def my_view(request):
    return {'project': 'quippy_wat'}

@view_config(route_name='home',
             renderer='templates/index.pt')
def home(request):
    logged_in = request.authenticated_userid
    quips = DBSession.query(Quip).order_by(Quip.created_date.desc()).all()
    form = Form(request, schema=QuipSchema())
    return {'quips': quips, 'form': FormRenderer(form), 'logged_in': logged_in}


@view_config(route_name='newquip',
             renderer='templates/index.pt',
             request_method='POST')
def newquip(request):
    logged_in = request.authenticated_userid
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
    logged_in = request.authenticated_userid
    key = request.params['q']
    if key == 'oldest':
        quips = DBSession.query(Quip).order_by(Quip.source_date.asc()).all()
    else:
        quips = DBSession.query(Quip).order_by(Quip.source_date.desc()).all()
    return{'quips': quips, 'logged_in': logged_in}
    
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

