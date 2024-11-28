import os
from email.message import Message
from enum import Enum
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, Literal

from restcraft.exceptions import RestCraftException

if TYPE_CHECKING:
    from tempfile import _TemporaryFileWrapper


class ParserState(Enum):
    START = "start"
    HEADER = "header"
    BODY = "body"
    BODY_END = "body-end"
    F_BODY = "fbody"
    F_BODY_END = "fbody-end"
    END = "end"


class DelimiterEnum(bytes, Enum):
    UNDEF = b""
    CRLF = b"\r\n"
    LF = b"\n"


EncodingErrors = Literal["strict", "ignore", "replace"]
FileFields = dict[str, list[dict[str, str]]]
FormFields = dict[str, list[str]]


class MultipartParser:
    """Parser for handling multipart form data.

    This class is responsible for parsing multipart form data from HTTP requests.
    It extracts form fields and files, supporting various content types and encoding
    options. The parser handles different states of parsing, such as processing
    headers, body, and file content. It provides methods to retrieve boundary and
    content length information, and raises exceptions for errors like missing headers
    or exceeding body size limits.
    """

    def __init__(
        self,
        environ: dict[str, Any],
        *,
        max_body_size: int = 2 * 1024 * 1024,
        chunk_size: int = 4096,
        encoding: str = "utf-8",
        encoding_errors: EncodingErrors = "strict",
        error_message: str = "Failed to parse request body",
    ) -> None:
        self._environ = environ
        self._state = ParserState.START
        self._cfield: dict[str, str] = {}
        self._ccontent = b""
        self._cstream: None | _TemporaryFileWrapper[bytes] = None
        self._max_body_size = max_body_size
        self._chunk_size = chunk_size
        self._encoding = encoding
        self._encoding_errors = encoding_errors
        self._error_message = error_message
        self._delimiter: DelimiterEnum = DelimiterEnum.UNDEF

        self.forms: FormFields = {}
        self.files: FileFields = {}

    @property
    def boundary(self) -> str:
        """Retrieve the boundary parameter from the Content-Type header.

        Returns:
            str: The boundary string used for multipart form data.

        Raises:
            RestCraftException: If the boundary parameter is missing from
            the Content-Type header.
        """

        ctype = self._environ.get("CONTENT_TYPE", "")

        message = Message()
        message["Content-Type"] = ctype

        boundary = message.get_param("boundary")

        if not boundary:
            raise RestCraftException(
                self._error_message,
                errors={"headers": "Missing boundary in Content-Type header"},
                status=400,
            )

        charset = message.get_param("charset")

        if charset:
            self._encoding = str(charset)

        return str(boundary)

    @property
    def content_length(self) -> int:
        """Retrieve the Content-Length header from the request environment.

        Returns:
            int: The value of the Content-Length header, or -1 if the header is
            missing.
        """

        return int(self._environ.get("CONTENT_LENGTH", -1))

    def parse(self):
        """Parse the request body.

        Raises:
            RestCraftException: if the request body is too large or invalid
        """

        if self.content_length < 0:
            raise RestCraftException(
                self._error_message,
                errors={"headers": "Missing Content-Length header"},
                status=400,
            )

        if self.content_length > self._max_body_size:
            raise RestCraftException(
                self._error_message,
                errors={"body": "Request body is too large"},
                status=413,
            )

        try:
            self._parse()
        except Exception as e:
            self._cleanup()
            raise e

        return self.forms, self.files

    def _detect_delimiter(self, buffer: bytes, boundary: bytes, blength: int):
        """Detect the line delimiter used in the request body.

        Given a buffer and a boundary, finds the first occurrence of the
        boundary and determines whether the line delimiter is CRLF or LF.

        Args:
            buffer: The buffer to search in.
            boundary: The boundary to search for.
            blength: The length of the boundary.

        Returns:
            The line delimiter used in the request body.

        Raises:
            ValueError: If the line delimiter cannot be determined.
        """

        idx = buffer.find(boundary)

        if idx < 0:
            raise ValueError("Unable to determine line delimiter.")

        if buffer[blength : blength + 2] == DelimiterEnum.CRLF:
            return DelimiterEnum.CRLF
        elif buffer[blength : blength + 1] == DelimiterEnum.LF:
            return DelimiterEnum.LF
        else:
            raise ValueError("Unable to determine line delimiter.")

    def _cleanup(self):
        """Clean up resources used during parsing.

        This method closes and removes the temporary file, clears temporary
        fields and content, and resets form and file storage.
        """

        if self._cstream is not None:
            if not self._cstream.closed:
                self._cstream.close()

            if os.path.exists(self._cstream.name):
                os.remove(self._cstream.name)

        self._cfield = {}
        self._ccontent = b""
        self._cstream = None
        self.forms = {}
        self.files = {}

    def _create_tempfile(self):
        """Create a temporary file with a predefined prefix and suffix.

        Returns:
            _TemporaryFileWrapper: A named temporary file object with the specified
            prefix and suffix, set to not be deleted automatically.
        """

        prefix = "restcraft-"
        suffix = ".tmp"

        return NamedTemporaryFile(
            prefix=prefix,
            suffix=suffix,
            delete=False,
        )

    def _on_start(self, buffer: bytes, boundary: bytes, blength: int):
        """Handle the initial parsing state when the boundary is detected.

        This method checks if the boundary is present in the buffer and, if found,
        updates the buffer to start after the boundary and changes the parser state
        to HEADER.

        Args:
            buffer: The byte buffer containing the multipart data.
            boundary: The boundary string used to delineate parts in the multipart data.
            blength: The length of the boundary.

        Returns:
            The updated buffer, starting after the boundary.
        """

        if (idx := buffer.find(boundary)) >= 0:
            buffer = buffer[idx + blength :]
            self._state = ParserState.HEADER

        return buffer

    def _on_header(self, buffer: bytes):
        """Handle the header parsing state when the delimiter is detected.

        This method checks if the delimiter is present in the buffer and, if found,
        partitions the buffer into headers and the remaining data. It then checks if
        the headers contain a filename parameter and sets the parser state accordingly.
        Finally, it processes the headers and returns the remaining buffer.

        Args:
            buffer: The byte buffer containing the multipart data.

        Returns:
            The updated buffer, starting after the delimiter.
        """

        delimiter = self._delimiter.value * 2

        if buffer.find(delimiter) >= 0:
            headers, _, buffer = buffer.partition(delimiter)

            if b"filename=" in headers:
                self._state = ParserState.F_BODY
            else:
                self._state = ParserState.BODY

            self._process_headers(headers)

        return buffer

    def _on_body(self, buffer: bytes, boundary: bytes):
        """Handle the body parsing state when the delimiter is detected.

        This method checks if the delimiter is present in the buffer and, if found,
        accumulates the body content and changes the parser state to BODY_END.

        Args:
            buffer: The byte buffer containing the multipart data.
            boundary: The boundary string used to delineate parts in the multipart data.

        Returns:
            The updated buffer, starting after the delimiter.
        """

        offset = 2 if self._delimiter == DelimiterEnum.CRLF else 1

        if (idx := buffer.find(boundary)) >= 0:
            self._ccontent += buffer[: idx - offset]
            buffer = buffer[idx:]
            self._state = ParserState.BODY_END

        return buffer

    def _on_body_end(self):
        """Handle the body end parsing state.

        This method accumulates the body content, decodes it to a string, and adds it
        to the forms dictionary. It also resets the content and field dictionaries.
        """

        self._state = ParserState.END

        name = self._cfield["name"]
        content = self._ccontent.decode(self._encoding, self._encoding_errors)

        if name in self.forms:
            self.forms[name].append(content)
        else:
            self.forms[name] = [content]

        self._cfield = {}
        self._ccontent = b""

    def _on_fbody(self, buffer: bytes, boundary: bytes, blength: int):
        """Handle the file body parsing state.

        This method writes the file content from the buffer to a temporary file
        stream until the boundary is detected. It adjusts the state to F_BODY_END
        when the boundary is found.

        Args:
            buffer: The byte buffer containing the multipart data.
            boundary: The boundary string used to delineate parts in the multipart data.
            blength: The length of the boundary.

        Returns:
            The updated buffer, starting after the boundary or retaining the last
            part of the buffer if the boundary isn't found.
        """

        offset = 2 if self._delimiter == DelimiterEnum.CRLF else 1

        if self._cstream is None:
            self._cstream = self._create_tempfile()

        if (idx := buffer.find(boundary)) >= 0:
            self._state = ParserState.F_BODY_END
            self._cstream.write(buffer[: idx - offset])
            buffer = buffer[idx:]
        else:
            self._cstream.write(buffer[:-blength])
            buffer = buffer[-blength:]

        self._cstream.flush()

        return buffer

    def _on_fbody_end(self):
        """Handle the end of a file body.

        This method writes any remaining data to the temporary file stream,
        closes the stream, and adds the file information to the request's files
        attribute. It resets the state to END and clears the current field and
        file stream.
        """

        self._state = ParserState.END

        if self._cstream is None:
            return

        self._cstream.close()

        name = self._cfield["name"]
        filename = self._cfield["filename"]
        ctype = self._cfield["content_type"]

        field = {
            "filename": filename,
            "tempfile": self._cstream.name,
            "content_type": ctype,
        }

        if name in self.files:
            self.files[name].append(field)
        else:
            self.files[name] = [field]

        self._cfield = {}
        self._cstream = None

    def _process_headers(self, data: bytes):
        """Process the headers of a part.

        This method decodes the header data, parses it into individual header fields,
        and extracts important parameters such as "filename", "content_type", and "name".
        It raises an exception if the "Content-Disposition" header is missing, as it is
        required to determine the disposition of the part.

        Args:
            data: The raw headers data as bytes.

        Raises:
            RestCraftException: If the "Content-Disposition" header is absent.
        """

        headers = [
            h.strip().decode(self._encoding, self._encoding_errors)
            for h in data.split(self._delimiter.value)
            if h
        ]

        message = Message()

        for h in headers:
            if ":" not in h:
                continue
            key, value = h.split(":", 1)
            message[key] = value

        if "Content-Disposition" not in message:
            raise RestCraftException(
                self._error_message,
                errors={"headers": "Missing Content-Disposition header"},
                status=400,
            )

        filename = message.get_param("filename", header="Content-Disposition")

        if filename:
            self._cfield["filename"] = str(filename)

        self._cfield["content_type"] = message.get_content_type()
        self._cfield["name"] = str(
            message.get_param("name", header="Content-Disposition")
        )

    def _parse(self):
        """Parse the request body.

        This method reads the request body and parses it. It accumulates the
        form data and files into the forms and files attributes of the
        MultipartParser instance.

        Raises:
            RestCraftException: If the request body is too large or invalid
        """

        boundary = f"--{self.boundary}".encode()
        boundary_end = f"--{self.boundary}--".encode()
        blength = len(boundary)
        buffer = b""
        read = self._environ["wsgi.input"].read
        chunk_size = self._chunk_size
        remaining = self.content_length

        while remaining > 0:
            c = read(min(chunk_size, remaining))
            remaining -= len(c)

            buffer += c

            if self._delimiter is DelimiterEnum.UNDEF:
                self._delimiter = self._detect_delimiter(buffer, boundary, blength)

            while buffer.find(boundary) >= 0:
                if self._state == ParserState.START:
                    buffer = self._on_start(buffer, boundary, blength)

                if self._state == ParserState.HEADER:
                    buffer = self._on_header(buffer)

                if self._state == ParserState.F_BODY:
                    buffer = self._on_fbody(buffer, boundary, blength)

                if self._state == ParserState.F_BODY_END:
                    self._on_fbody_end()

                if self._state == ParserState.BODY:
                    buffer = self._on_body(buffer, boundary)

                if self._state == ParserState.BODY_END:
                    self._on_body_end()

                if self._state == ParserState.END:
                    if buffer.startswith(boundary_end):
                        break
                    self._state = ParserState.START
