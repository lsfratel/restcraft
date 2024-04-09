import unittest
from io import BytesIO

from restipy.core.exceptions import MalformedBodyException
from restipy.core.request import Request

app = object()


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
        'restipy.app': app,
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
        self.assertEqual(self.req.app, app)

    def test_request_json_body(self):
        body = {'firstname': 'john', 'lastname': 'doe'}
        self.assertDictEqual(self.req.json, body)  # type: ignore

    def test_request_set_json_body(self):
        self.req.set_json = {'new_dict': True}
        self.assertDictEqual(self.req.json, {'new_dict': True})  # type: ignore

    def test_request_json_body_error(self):
        self.req.env['wsgi.input'] = BytesIO(b'error')
        with self.assertRaises(MalformedBodyException) as e:
            _ = self.req.json
        resp = e.exception.to_response()
        self.assertEqual(resp.status, 400)
        self.assertDictEqual(
            resp.data,
            {'code': 'MALFORMED_BODY', 'error': 'Malformed JSON body.'},
        )

    def test_request_form_body(self):
        self.req.env['wsgi.input'] = BytesIO(b'firstname=john&lastname=doe')
        body = {'firstname': ['john'], 'lastname': ['doe']}
        self.assertDictEqual(self.req.form, body)  # type: ignore

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
        query = {'a': ['1'], 'name': ['lucas']}
        self.assertDictEqual(self.req.query, query)  # type: ignore

    def test_request_host(self):
        host = 'localhost:8080'
        self.assertEqual(self.req.host, host)

    def test_request_content_type_charset(self):
        charset = 'utf-8'
        self.assertEqual(self.req.charset, charset)

    def test_request_length(self):
        length = len(b'{"firstname": "john", "lastname": "doe"}')
        self.assertEqual(self.req.length, length)

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
