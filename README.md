# RestCraft

RestCraft is a lightweight, modular framework designed to build modern web applications in Python. It provides essential tools and components to manage HTTP requests, responses, routing, and middleware, allowing you to focus on building features without being overwhelmed by boilerplate code.

### Key Features

- **Zero External Dependencies**: RestCraft is built entirely with Python's standard library, ensuring a minimal footprint and maximum compatibility.
- **Powerful Routing System**: Support for dynamic and static routes, route merging, and modular blueprints for better organization.
- **Request and Response Handling**: A clean and extensible API to manage HTTP requests, responses, cookies, and headers.
- **Pluggable Architecture**: Add plugins to extend functionality with fine-grained control over their application.
- **Built-in Middleware for CORS**: Enable Cross-Origin Resource Sharing with a simple plugin.
- **Exception Handling**: Centralized error handling with customizable exception responses.

Whether you're building a simple API or a large-scale application, RestCraft gives you the flexibility and control you need while staying lightweight and dependency-free.

## Installation

To install **RestCraft**, just pip install:

```bash
pip install restcraft
```

## Getting Started

Here’s a quick example to set up and run a simple **RestCraft** application:

```python
from restcraft import RestCraft, Router, JSONResponse
from restcraft.views import metadata

from .config import configuration

# Define your views
class HelloWorldView:
    @metadata(methods=["GET"])
    def get(self):
        return JSONResponse({"message": "Hello, World!"})

# Set up the application
app = RestCraft(config=configuration)

# Set up the router
router = Router()
router.add_route("/hello", HelloWorldView())
app.register_router(router)

# Run the application using a WSGI server
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    server = make_server("127.0.0.1", 8000, app)
    print("Serving on http://127.0.0.1:8000")
    server.serve_forever()
```

## Core Concepts

### Routes

RestCraft provides a powerful routing system to map URL paths to specific views. The `Router` class allows you to register routes, handle dynamic parameters, and merge routers for modular and reusable routing logic.

#### Adding Routes

To add a route, use the `add_route` method. Specify the path and the corresponding view object or class:

```python
from restcraft.http.router import Router
from restcraft.http.response import JSONResponse
from restcraft.views import metadata

class MyView:
    @metadata(methods=["GET"])
    def hello(self):
        return JSONResponse({"message": "Hello, World!"})

router = Router()
router.add_route("/hello", MyView())
```

#### Dynamic Routes

Dynamic segments in paths are defined with a `<` prefix and `>` suffix. Dynamic routes allow you to capture parts of the URL and pass them as parameters to the handler:

```python
class UserView:
    @metadata(methods=["GET"])
    def get_user(self, id):
        return JSONResponse({"user_id": id})

router.add_route("/user/<id>", UserView())
router.add_route(r"/user/<id:\d+>", UserView())

# Example:
# GET /user/42 -> {"user_id": "42"}
```

#### Merging Routers

The `merge` function allows you to combine multiple routers into a single router. This enables modular routing, similar to blueprints in other frameworks, making it easy to organize your application by grouping related routes.

```python
# Define a "users" module
users_router = Router(prefix="/users")

class UserView:
    @metadata(methods=["GET"])
    def list_users(self):
        return JSONResponse({"users": []})

    @metadata(methods=["POST"])
    def create_user(self):
        return JSONResponse({"message": "User created"})

users_router.add_route("/", UserView())

# Define a "products" module
products_router = Router(prefix="/products")

class ProductView:
    @metadata(methods=["GET"])
    def list_products(self):
        return JSONResponse({"products": []})

products_router.add_route("/", ProductView())

# Merge modules into the main router
app_router = Router()
app_router.merge(users_router)
app_router.merge(products_router)

# Example:
# GET /users -> {"users": []}
# GET /products -> {"products": []}
```

### Request Handling

Access request properties like headers, query parameters, JSON payloads, forms, and file uploads:

```python
from restcraft.http import request

class UserView:
    @metadata(methods=["POST"])
    def create(self):
        data = request.json
        return JSONResponse({"received": data})
```

### Plugins

Extend functionality using plugins. Plugins in RestCraft are middleware-like components that can modify the behavior of request handlers. Each plugin can be selectively applied to specific methods by using the `metadata` decorator.

#### Using Plugins

To register a plugin, use the `register_plugin` method of the `RestCraft` application:

```python
from restcraft.contrib.plugins.cors_plugin import CORSPlugin

plugin = CORSPlugin(allow_origins=["http://example.com"])
app.register_plugin(plugin)
```

#### Controlling Plugin Execution with Metadata

The `metadata` decorator allows you to specify which plugins should run (or be excluded) for a particular method. By default, all plugins run on all methods unless specified otherwise.

- **Include Plugins**: List plugin names to explicitly allow them.
- **Exclude Plugins**: Prefix the plugin name with `-` to exclude it.

Here’s an example:

```python
from restcraft.http.response import JSONResponse
from restcraft.views import metadata

class MyView:
    # Allow all plugins (default behavior)
    @metadata(methods=["GET"])
    def all_plugins_allowed(self):
        return JSONResponse({"message": "All plugins are allowed"})

    # Only allow 'cors_plugin' to run
    @metadata(methods=["POST"], plugins=["cors_plugin"])
    def only_cors_plugin(self):
        return JSONResponse({"message": "Only CORS plugin will run"})

    # Exclude 'auth_plugin'
    @metadata(methods=["DELETE"], plugins=["...", "-auth_plugin"])
    def exclude_auth_plugin(self):
        return JSONResponse({"message": "All plugins except 'auth_plugin' will run"})
```

#### Writing Your Own Plugin

To create a custom plugin, subclass the `Plugin` class and implement the `before_handler` or `before_route` method:

```python
from restcraft.plugin import Plugin

class CustomHeaderPlugin(Plugin):
    name = "custom_header_plugin"

    def before_handler(self, handler, metadata):
        def wrapper(*args, **kwargs):
            response = handler(*args, **kwargs)
            response.headers["X-Custom-Header"] = "My Custom Value"
            return response
        return wrapper
```

Register your plugin with the application:

```python
plugin = CustomHeaderPlugin()
app.register_plugin(plugin)
```

#### Plugin Execution Order

Plugins are applied in the order they are registered in the application. To control execution order, register plugins in the desired sequence:

```python
app.register_plugin(PluginA())
app.register_plugin(PluginB())
```

## File Uploads

RestCraft handles file uploads efficiently, writing large files to disk-backed temporary storage. Here's how you can access uploaded files:

```python
class FileUploadView:
    @metadata(methods=["POST"])
    def upload(self):
        file_data = request.files.get("file")
        return JSONResponse({
            "filename": file_data["filename"],
            "content_type": file_data["content_type"],
        })
```

## Cookies

RestCraft includes a powerful and flexible cookie management system inspired by [Remix.run](https://remix.run). With RestCraft, you can easily create, parse, sign, and validate cookies, enabling secure state management for your web applications.

### Key Features

- **Serialization and Parsing**: Effortlessly serialize Python objects into cookies and parse them back into Python objects.
- **Signed Cookies**: Use secret keys to sign cookies, ensuring their integrity and protecting against tampering.
- **Expiration and Max-Age**: Automatically manage cookie expiration with built-in support for `Expires` and `Max-Age` attributes.
- **Secure Defaults**: Cookies are configured to be `HttpOnly` and `Secure` by default, ensuring they are protected from client-side scripts and transmitted only over HTTPS.

### Example Usage

#### Creating and Serializing a Cookie

```python
from restcraft.http import Cookie

# Create a new cookie with secure options
cookie = Cookie("user_session", options={"secrets": ["my_secret_key"], "secure": True})

class MyView:

    @metadata(methods=["GET"])
    def list(self):
        # read
        user_info = cookie.parse(request.headers["cookie"])

        # set
        return JSONResponse(data, headers={"Set-Cookie": cookie.serialize(user_info, overrides={"max_age": 60})})
```

## Custom Exception Handling

Define custom exception handlers for your application:

```python
from restcraft.exceptions import RestCraftException

@app.register_exception(RestCraftException)
def handle_restcraft_exception(exc):
    return JSONResponse({"error": exc.message}, status=exc.status)
```

## Contributing

Contributions are welcome! If you'd like to improve RestCraft, follow these steps:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and write tests.
4. Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgements

Special thanks to all contributors and the Python community for inspiring this project.
