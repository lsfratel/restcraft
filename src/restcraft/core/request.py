from __future__ import annotations

import email
import email.parser
import email.policy
import io
import json
import shutil
import tempfile
import typing as t
from email.message import Message
from urllib.parse import parse_qsl, urljoin

from restcraft.conf import settings
from restcraft.core.exceptions import (
    MalformedBody,
    RequestBodyTooLarge,
)
from restcraft.utils.helpers import UploadedFile, env_to_h

if t.TYPE_CHECKING:
    from restcraft.core.application import RestCraft


__all__ = ('Request',)


class Request:
    """
    Represents an HTTP request in the RestCraft framework.

    The `Request` class provides properties and methods to access and parse
    various aspects of an HTTP request, such as headers, query parameters, form
    data, JSON data, and uploaded files.

    Attributes:
        env (Dict): The WSGI environment dictionary.
        ctx (Dict[str, Any]): A dictionary for storing custom context data.

    Properties:
        app (RestCraft): The RestCraft application associated with the request.
        params (Dict[str, Any]): The parameters of the request.
        json (Optional[Dict[str, Any]]): The parsed JSON data from the request
            body.
        form (Optional[Dict[str, str]]): The form data of the request.
        files (Optional[Dict[str, UploadedFile]]): The uploaded files from the
            request.
        header (Dict[str, str]): The headers of the request.
        origin (str): The origin of the request.
        url (str): The complete URL of the request.
        href (str): The complete URL with the query string.
        method (str): The HTTP request method.
        path (str): The path of the request.
        query (Optional[Dict[str, List[Any]]]): The query parameters of the
            request.
        host (str): The HTTP host of the request.
        charset (Optional[str]): The character encoding of the request's
            content type.
        content_length (int): The length of the request's content body.
        protocol (str): The protocol (HTTP or HTTPS) used for the request.
        secure (bool): Whether the request was made over a secure (HTTPS)
            connection.
        accept (Optional[str]): The value of the "Accept" HTTP header.
        content_type (str): The content type of the request's content body.

    Methods:
        __init__(self, environ: Dict, params: Dict = {}): Initializes a new
            instance of the Request class.
        _read_body(self) -> Generator[bytes, None, None]: Reads the request
            body in chunks.
        _parse_url_encoded_form(self) -> Optional[Dict[str, Any]]: Parses the
            URL-encoded form data from the request body.
        _get_multipart_message(self) -> Message: Parses the multipart message
            from the request body.
        _parse_multipart_files(self) -> Optional[Dict[str, UploadedFile]]:
            Parses the multipart files from the request body.
        _parse_multipart_form(self) -> Optional[Dict[str, Any]]: Parses the
            multipart form data from the request body.
        _parse_json_data(self) -> Optional[Dict[str, Any]]: Parses the request
            body as JSON data.
        set_params(self, params: Dict): Sets the parameters for the request.
        __repr__(self) -> str: Returns a string representation of the request
            object.
    """

    __slots__ = (
        '_params',
        '_headers',
        '_files',
        '_form',
        'env',
        'ctx',
    )

    def __init__(self, environ: t.Dict, params: t.Dict = {}) -> None:
        self.env = environ
        self.ctx: t.Dict[str, t.Any] = {}

        self._params = params
        self._headers: t.Any = None
        self._files: t.Dict[str, UploadedFile] = {}
        self._form: t.Dict[str, t.Any] = {}

    def _read_body(self) -> t.Generator[bytes, None, None]:
        """
        Reads the request body in chunks, ensuring the total size does not
        exceed the maximum allowed body size.

        Yields:
            bytes: The next chunk of the request body.

        Raises:
            RequestBodyTooLarge: If the total size of the request body exceeds
                the maximum allowed body size.
        """
        if self.method not in ('POST', 'PUT', 'PATCH'):
            return None

        content_length = self.content_length

        max_body_size = settings.MAX_BODY_SIZE

        if content_length > max_body_size:
            raise RequestBodyTooLarge()

        input_stream = self.env['wsgi.input']
        readbytes = 0

        while readbytes < content_length:
            chunk = input_stream.read(
                min(64 * 1024, content_length - readbytes)
            )
            if not chunk:
                break
            yield chunk
            readbytes += len(chunk)
            if readbytes > max_body_size:
                raise RequestBodyTooLarge()

    def _parse_url_encoded_form(self) -> t.Optional[t.Dict[str, t.Any]]:
        """
        Parses the URL-encoded form data from the request body.

        Returns:
            Optional[Dict[str, Any]]: The parsed form data, or `None` if there
                is no form data.

        Raises:
            MalformedBody: If the request body cannot be parsed as URL-encoded
                form data.
        """
        if self._form:
            return self._form

        body = b''

        for chunk in self._read_body():
            body += chunk

        try:
            self._form = dict(parse_qsl(body.decode()))
        except Exception as e:
            raise MalformedBody() from e

        if self._form:
            return self._form

    def _get_multipart_message(self) -> Message:
        """
        Parses the multipart message from the request body.

        Returns:
            Message: The parsed multipart message.
        """
        parser = email.parser.BytesFeedParser(policy=email.policy.HTTP)
        parser.feed(('content-type: %s\r\n' % self.content_type).encode())
        parser.feed('\r\n'.encode())

        for chunk in self._read_body():
            parser.feed(chunk)

        return parser.close()

    def _parse_multipart_files(self) -> t.Optional[t.Dict[str, UploadedFile]]:
        """
        Parses the multipart files from the request body.

        Returns:
            Optional[Dict[str, UploadedFile]]: A dictionary of uploaded files,
                where the keys are the field names and the values are
                `UploadedFile` instances. If there are no multipart files,
                `None` is returned.
        """
        if self._files:
            return self._files

        message = self._get_multipart_message()

        if not message.is_multipart():
            return

        for part in message.iter_parts():  # type: ignore
            if not part.get_filename():
                continue

            name = part.get_param('name', header='content-disposition')

            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                shutil.copyfileobj(
                    io.BytesIO(part.get_payload(decode=True)), tmp_file
                )
                self._files[name] = UploadedFile(
                    filename=part.get_filename(),
                    content_type=part.get_content_type(),
                    filepath=tmp_file.name,
                )

        if not self._files:
            return

        return self._files

    def _parse_multipart_form(self) -> t.Optional[t.Dict[str, t.Any]]:
        """
        Parses the multipart form data from the request body.

        Returns:
            Optional[Dict[str, Any]]: A dictionary of form field names and
                their corresponding values. If there is no multipart form data,
                `None` is returned.
        """
        if self._form:
            return self._form

        message = self._get_multipart_message()

        if not message.is_multipart():
            return

        for part in message.iter_parts():  # type: ignore
            if part.get_filename():
                continue

            name = part.get_param('name', header='content-disposition')
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                payload = payload.decode()
            self._form[name] = payload

        if self._form:
            return self._form

    def _parse_json_data(self) -> t.Optional[t.Dict[str, t.Any]]:
        """
        Parses the request body as JSON data and returns a dictionary
        containing the parsed data.

        If the request content type is not "application/json" or
        "application/json-rpc", this method returns `None`.

        If the request body is empty, this method returns `None`.

        If there is an error parsing the JSON data, this method raises a
        `MalformedBody` exception.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the parsed JSON
                data, or `None` if the request body is not JSON.
        """
        if self._form:
            return self._form

        ctype = self.content_type.lower().split(';')[0]

        if ctype not in ('application/json', 'application/json-rpc'):
            return

        body = b''

        for chunk in self._read_body():
            body += chunk

        if not body:
            return

        try:
            self._form = json.loads(body.decode())
        except Exception as e:
            raise MalformedBody() from e

        if self._form:
            return self._form

    @property
    def app(self) -> RestCraft:
        """
        Returns the RestCraft application associated with the request.

        RestCraft: The RestCraft application.
        """
        return self.env['restcraft.app']

    @property
    def params(self) -> t.Dict[str, t.Any]:
        """
        Returns the parameters of the request.

        Dict[str, Any]: A dictionary containing the parameters of the request.
        """
        return self._params

    @params.setter
    def set_params(self, params: t.Dict):
        """
        Set the parameters for the request.

        Args:
            params (dict): A dictionary containing the parameters to be set.
        """
        self._params = params

    @property
    def json(self) -> t.Optional[t.Dict[str, t.Any]]:
        """
        Returns the parsed JSON data from the request body, if present.

        Optional[Dict[str, Any]]: A dictionary containing the parsed JSON data,
            or None if no JSON data is present.
        """
        return self._parse_json_data()

    @property
    def form(self) -> t.Optional[t.Dict[str, str]]:
        """
        Returns the form data of the request, if available.

        If the request content type is 'multipart/', the form data is parsed
        using the `_parse_multipart_form()` method. Otherwise, the form data
        is parsed using the `_parse_url_encoded_form()` method.

        Optional[Dict[str, str]]: A dictionary containing the form data, or
            None if no form data is available.
        """
        if self.content_type.startswith('multipart/'):
            return self._parse_multipart_form()
        return self._parse_url_encoded_form()

    @property
    def files(self) -> t.Optional[t.Dict[str, UploadedFile]]:
        """
        Returns a dictionary containing the uploaded files from the request.

        The dictionary maps the field names to the corresponding UploadedFile
        objects. If there are no uploaded files, this method returns None.

        Returns:
            Optional[Dict[str, UploadedFile]]: A dictionary containing the
                uploaded files, or None if there are no uploaded files.
        """
        return self._parse_multipart_files()

    @property
    def header(self) -> t.Dict[str, str]:
        """
        Returns a dictionary containing the headers of the request.

        The headers are extracted from the environment variables that start
        with 'HTTP_'. The keys in the returned dictionary are the header names
        without the 'HTTP_' prefix, and the values are the corresponding header
        values.

        Returns:
            Dict[str, str]: A dictionary containing the request headers.
        """

        if self._headers:
            return self._headers

        self._headers = {
            env_to_h(k)[5:]: v
            for k, v in self.env.items()
            if k.startswith('HTTP_')
        }

        return self._headers

    @property
    def origin(self) -> str:
        """
        Returns the origin of the request.

        The origin is constructed by combining the protocol and host of the
        request.

        Returns:
            str: The origin of the request.
        """
        return f'{self.protocol}://{self.host}'.lower()

    @property
    def url(self) -> str:
        """
        Constructs and returns the complete URL by joining the origin and path
        of the request.

        Returns:
            str: The complete URL of the request.
        """
        return urljoin(self.origin, self.path).rstrip('/')

    @property
    def href(self) -> str:
        """
        Returns the complete URL with the query string.

        Returns:
            str: The complete URL with the query string.
        """
        return f'{self.url}?{self.env.get("QUERY_STRING", "")}'

    @property
    def method(self) -> str:
        """
        Returns the HTTP request method.

        Returns:
            str: The HTTP request method. Defaults to 'GET' if not specified
                in the environment.
        """
        return self.env.get('REQUEST_METHOD', 'GET').upper()

    @property
    def path(self) -> str:
        """
        Get the path of the request.

        Returns:
            str: The path of the request.
        """
        return self.env.get('PATH_INFO', '/')

    @property
    def query(self) -> t.Optional[t.Dict[str, t.List[t.Any]]]:
        """
        Constructs and returns a dictionary of query parameters from the
        request's query string.

        Returns:
            Optional[Dict[str, List[Any]]]: A dictionary of query parameters,
                or `None` if the query string is empty.
        """
        qs = self.env.get('QUERY_STRING')
        if qs is None:
            return
        return dict(parse_qsl(qs))

    @property
    def host(self) -> str:
        """
        Returns the HTTP host of the request.

        Returns:
            str: The HTTP host of the request, or an empty string if not
                available.
        """
        return self.env.get('HTTP_HOST', '')

    @property
    def charset(self, default='utf-8') -> t.Optional[str]:
        """
        Returns the character encoding of the request's content type, or a
        default value if the content type is not available or does not specify
        a charset.

        Returns:
            Optional[str]: The character encoding of the request's content
                type, or the default value if the content type is not available
                or does not specify a charset.
        """
        if not self.content_type:
            return default

        for part in self.content_type.split(';'):
            if 'charset=' in part:
                return part.split('=')[1].strip()

        return default

    @property
    def content_length(self) -> int:
        """
        Returns the length of the request's content body as an integer.

        Returns:
            int: The length of the request's content body, or 0 if the content
                length is not available.
        """
        return int(self.env.get('CONTENT_LENGTH', '0'))

    @property
    def protocol(self) -> str:
        """
        Returns the protocol (HTTP or HTTPS) used for the request.

        Returns:
            str: The protocol used for the request, either "HTTP" or "HTTPS".
        """
        return self.env.get('wsgi.url_scheme', 'http').upper()

    @property
    def secure(self) -> bool:
        """
        Returns whether the request was made over a secure (HTTPS) connection.

        Returns:
            bool: True if the request was made over HTTPS, False otherwise.
        """
        return self.protocol == 'HTTPS'

    @property
    def accept(self) -> t.Optional[str]:
        """
        Returns the value of the "Accept" HTTP header, or None if the header is
        not present.

        The "Accept" header specifies the media types that the client is able
        to understand. This method returns the value of this header, converted
        to lowercase, or None if the header is not present in the request.

        Returns:
            Optional[str]: The value of the "Accept" HTTP header, converted to
                lowercase, or None if the header is not present.
        """
        accept = self.env.get('HTTP_ACCEPT')
        if accept:
            return accept.lower()
        return accept

    @property
    def content_type(self) -> str:
        """
        Returns the content type of the request's content body.

        Returns:
            str: The content type of the request's content body, or an empty
                string if the content type is not available.
        """
        return self.env.get('CONTENT_TYPE', '')

    def __repr__(self) -> str:
        """
        Returns a string representation of the request object, including the
        HTTP method and the request path.

        Returns:
            str: A string representation of the request object in the format
                "<Request GET /hello>".
        """
        return f'<Request {self.method} {self.path}>'
