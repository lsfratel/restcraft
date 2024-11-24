import base64
import hashlib
import hmac
import json
import random
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from typing import Any


def make_expires(date: datetime | int):
    if isinstance(date, datetime):
        return date.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
    elif isinstance(date, int):
        return (datetime.now() + timedelta(seconds=date)).strftime(
            "%a, %d-%b-%Y %H:%M:%S GMT"
        )
    else:
        raise ValueError("Date must be date or seconds")


class Cookie:
    def __init__(self, name: str, options: dict[str, Any] = {}):
        self.name = name
        self.options = {
            "path": "/",
            "max_age": 3600,
            "same_site": "Lax",
            "secrets": [],
            "secure": False,
            "http_only": True,
            **options,
        }

        if "secrets" in self.options:
            if len(self.options["secrets"]) == 0:
                del self.options["secrets"]

    def _sign(self, data: str, secret: str):
        signature = hmac.new(secret.encode(), data.encode(), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(signature).decode()

    def _verify(self, data: str, signature: str):
        for secret in self.options["secrets"]:
            expected_signatue = self._sign(data, secret)
            if hmac.compare_digest(expected_signatue, signature):
                return True
        return False

    def serialize(self, data: Any, overrides: dict[str, Any] = {}):
        options = {**self.options, **overrides}

        new_data = json.dumps(data)

        if "secrets" in options and len(options["secrets"]) > 0:
            signature = self._sign(new_data, random.choice(options["secrets"]))
            new_data = base64.urlsafe_b64encode(new_data.encode()).decode()
            new_data = f"{new_data}.{signature}"

        cookie = SimpleCookie()
        cookie[self.name] = new_data

        if options.get("expires"):
            cookie[self.name]["Expires"] = make_expires(options["expires"])

        if options.get("max_age"):
            cookie[self.name]["Max-Age"] = options["max_age"]

        if options.get("path"):
            cookie[self.name]["Path"] = options["path"]

        if options.get("http_only"):
            cookie[self.name]["HttpOnly"] = options["http_only"]

        if options.get("secure"):
            cookie[self.name]["Secure"] = options["secure"]

        if options.get("same_site"):
            cookie[self.name]["SameSite"] = options["same_site"]

        return cookie.output(header="", sep="").strip()

    def parse(self, header: str | None):
        cookie = SimpleCookie(header)

        if self.name not in cookie:
            return None

        cookie_value = cookie[self.name].value
        if "secrets" not in self.options:
            try:
                return json.loads(cookie_value)
            except Exception:
                return None

        try:
            data, signature = cookie_value.rsplit(".", 1)
            data = base64.urlsafe_b64decode(data).decode()
            if not self._verify(data, signature):
                return None
            return json.loads(data)
        except Exception:
            return None
