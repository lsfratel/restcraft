import os
from email.message import Message
from enum import Enum
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper
from typing import Any, Literal

from restcraft.exceptions import RestCraftException


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
        return int(self._environ.get("CONTENT_LENGTH", -1))

    def parse(self):
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
        prefix = "restcraft-"
        suffix = ".tmp"

        return NamedTemporaryFile(
            prefix=prefix,
            suffix=suffix,
            delete=False,
        )

    def _on_start(self, buffer: bytes, boundary: bytes, blength: int):
        if (idx := buffer.find(boundary)) >= 0:
            buffer = buffer[idx + blength :]
            self._state = ParserState.HEADER

        return buffer

    def _on_header(self, buffer: bytes):
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
        offset = 2 if self._delimiter == DelimiterEnum.CRLF else 1

        if (idx := buffer.find(boundary)) >= 0:
            self._ccontent += buffer[: idx - offset]
            buffer = buffer[idx:]
            self._state = ParserState.BODY_END

        return buffer

    def _on_body_end(self):
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
