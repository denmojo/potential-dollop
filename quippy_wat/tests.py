import unittest

from pyramid import testing
from pyramid.paster import get_appsettings
settings = get_appsettings('test.ini', name='main')

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'quippy_wat')


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from quippy_wat import main
        app = main(global_config = None, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/quips', status=200)
        self.assertTrue(b'Quips' in res.body)
