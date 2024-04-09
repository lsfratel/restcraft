from restipy.wsgi import get_wsgi_application
from test_app import settings

application = get_wsgi_application(settings)
