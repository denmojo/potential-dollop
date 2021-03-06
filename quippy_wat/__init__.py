from pyramid.config import Configurator
from sqlalchemy import engine_from_config

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
    config.add_static_view('quips/static', 'static', cache_max_age=3600)
    config.add_route('my_view', '/')
    config.add_route('home', '/quips')
    config.add_route('newquip', '/quips/newquip')
    config.add_route('sorted', '/quips/sort')
    config.add_route('quip_autocomplete', '/quips/autocomplete')
    config.scan()
    return config.make_wsgi_app()
