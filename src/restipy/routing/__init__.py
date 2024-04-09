from http import client as httplib

HTTP_CODES = httplib.responses.copy()
HTTP_CODES[418] = "I'm a teapot"
HTTP_CODES[428] = 'Precondition Required'
HTTP_CODES[429] = 'Too Many Requests'
HTTP_CODES[431] = 'Request Header Fields Too Large'
HTTP_CODES[451] = 'Unavailable For Legal Reasons'
HTTP_CODES[511] = 'Network Authentication Required'
HTTP_STATUS_LINES = {k: '%d %s' % (k, v) for (k, v) in HTTP_CODES.items()}
