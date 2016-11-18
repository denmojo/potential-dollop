from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from .security import groupfinder

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_mailer')
    
    # Security policies
    authn_policy = AuthTktAuthenticationPolicy(
        settings['quips.secret'],
        hashalg='sha512')
    # TODO: AuthZ configuration
    #authn_policy = AuthTktAuthenticationPolicy(
    #    settings['quips.secret'], callback=groupfinder,
    #    hashalg='sha512')

    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    
    config.add_static_view('quips/static', 'static', cache_max_age=3600)
    config.add_route('my_view', '/')
    config.add_route('home', '/quips')
    config.add_route('login', '/quips/login')
    config.add_route('logout', '/quips/logout')
    config.add_route('create_account', '/quips/create_account')
    config.add_route('newquip', '/quips/newquip')
    config.add_route('sorted', '/quips/sort')
    config.add_route('quip_autocomplete', '/quips/autocomplete')
    config.add_route('verify_account', '/quips/verify_account')
    config.scan()
    return config.make_wsgi_app()
