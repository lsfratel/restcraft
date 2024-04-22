import unittest
from io import BytesIO

from restcraft.conf import settings
from restcraft.core import Request
from restcraft.core.exceptions import HTTPException


class Settings:
    MAX_BODY_SIZE = 24 * 1024


class App:
    config = Settings()


class TestRequest(unittest.TestCase):
    environ = {
        'PATH_INFO': '/hello',
        'REQUEST_METHOD': 'PATCH',
        'CONTENT_TYPE': 'application/json; charset=utf-8',
        'CONTENT_LENGTH': str(
            len(b'{"firstname": "john", "lastname": "doe"}')
        ),
        'HTTP_AUTHORIZATION': 'Bearer',
        'HTTP_HOST': 'localhost:8080',
        'HTTP_ACCEPT': '*/*',
        'QUERY_STRING': 'a=1&name=lucas',
        'restcraft.app': App(),
        'wsgi.input': BytesIO(b'{"firstname": "john", "lastname": "doe"}'),
        'wsgi.url_scheme': 'http',
    }
    params = {'param_1': 1, 'param_2': 3}

    def setUp(self) -> None:
        self.req = Request(
            environ=self.environ.copy(),
            params=self.params.copy(),
        )

    def test_request_params(self):
        self.assertDictEqual(self.req.params, self.params)

    def test_request_set_params(self):
        param = {'pk': 1}
        self.req.set_params = param
        self.assertDictEqual(self.req.params, param)

    def test_request_app(self):
        self.assertIsInstance(self.req.app, object)

    def test_request_json_body(self):
        form = self.req.json

        assert form is not None

        self.assertEqual(form.get('firstname'), 'john')
        self.assertEqual(form.get('lastname'), 'doe')

    def test_request_json_body_error(self):
        self.req.env['wsgi.input'] = BytesIO(b'error')
        with self.assertRaises(HTTPException) as e:
            _ = self.req.json
        resp = e.exception
        self.assertEqual(resp.status_code, 400)
        self.assertDictEqual(
            resp.body,
            {
                'code': 'MALFORMED_BODY',
                'message': 'The request body could not be parsed as JSON.',
            },
        )

    def test_request_form_body(self):
        string = 'firstname=john&lastname=doe&lastname=lfs&number=1&arroz=2'
        self.req.env['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        self.req.env['CONTENT_LENGTH'] = str(len(string))
        self.req.env['wsgi.input'] = BytesIO(string.encode())

        form = self.req.form

        assert form is not None

        self.assertEqual(form.get('firstname'), 'john')
        self.assertEqual(form.get('lastname', index=0), 'doe')
        self.assertEqual(form.get('lastname', index=1), 'lfs')
        self.assertEqual(form.get('number', type=int), 1)

    def test_request_header(self):
        headers = {
            'authorization': 'Bearer',
            'host': 'localhost:8080',
            'accept': '*/*',
        }
        self.assertDictEqual(self.req.header, headers)

    def test_request_origin(self):
        origin = 'http://localhost:8080'
        self.assertEqual(self.req.origin, origin)

    def test_request_url(self):
        url = 'http://localhost:8080/hello'
        self.assertEqual(self.req.url, url)

    def test_request_href(self):
        href = 'http://localhost:8080/hello?a=1&name=lucas'
        self.assertEqual(self.req.href, href)

    def test_request_method(self):
        self.assertEqual(self.req.method, 'PATCH')

    def test_request_path(self):
        self.assertEqual(self.req.path, '/hello')

    def test_request_query(self):
        qs = self.req.query

        assert qs is not None

        self.assertEqual(qs.get('a'), '1')
        self.assertEqual(qs.get('name'), 'lucas')

    def test_request_host(self):
        host = 'localhost:8080'
        self.assertEqual(self.req.host, host)

    def test_request_content_type_charset(self):
        charset = 'utf-8'
        self.assertEqual(self.req.charset, charset)

    def test_request_content_length(self):
        length = len(b'{"firstname": "john", "lastname": "doe"}')
        self.assertEqual(self.req.content_length, length)

    def test_request_protocol(self):
        protocol = 'HTTP'
        self.assertEqual(self.req.protocol, protocol)

    def test_request_secure(self):
        self.assertEqual(self.req.secure, False)
        self.req.env['wsgi.url_scheme'] = 'https'
        self.assertEqual(self.req.secure, True)

    def test_request_accept(self):
        accept = '*/*'
        self.assertEqual(self.req.accept, accept)

    def test_request_content_type(self):
        content_type = 'application/json; charset=utf-8'
        self.assertEqual(self.req.content_type, content_type)

    def test_request_max_body_size(self):
        settings.MAX_BODY_SIZE = 10  # type: ignore
        with self.assertRaises(HTTPException) as e:
            _ = self.req.json
        resp = e.exception
        self.assertEqual(resp.status_code, 413)
        self.assertDictEqual(
            resp.body,
            {
                'code': 'REQUEST_BODY_TOO_LARGE',
                'message': 'Request body too large.',
            },
        )
