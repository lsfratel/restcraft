# RestiPy WSGI Framework

RestiPy is a lightweight WSGI framework for Python, following the principles of minimalist design, RestiPy provides a solid foundation for developing web applications.

## Framework Structure

RestiPy is divided into two main parts:

- **Framework:** Provides the tools, libraries, and base structures needed for web application development. This includes mechanisms for routing requests, handling responses, and a robust middleware system.

- **Project:** The specific application created by the developer, using the framework. Here, the developer can define routes, views, middlewares, and any other application-specific logic.

## Main Features

### Settings

- **Configuration File:** Centralizes project settings, allowing the definition of directories for dependencies such as views and middleware folders.

### Middlewares

- **Early Return:** Allows for the early interruption and return of a request before reaching the final handler.
- **Before Route:** Functions executed before a route is matched, useful for pre-processing logic.
- **Before Handler:** Executed after route matching and before the handler, ideal for validations and authorizations.
- **After Handler:** Invoked after the route handler's execution, allowing for modification of the response before it is sent to the client.
- **Request/Response Modification:** Facilitates the alteration of response and request objects at any stage of the process.

### Views

- **Classes:** Uses a class-based system to define views, providing an organized and reusable structure.
- **Defines Routes:** Allows for the explicit definition of routes within view classes.
- **Defines Handlers:** Associates each route with a specific handler, facilitating the organization of request handling logic.

### Routes

- **Regular Expressions:** Uses regular expressions to define routes, offering flexibility and precision in URL pattern matching.

### Project Example
[https://github.com/lsfratel/restipy/tree/main/tests/test_app](https://github.com/lsfratel/restipy/tree/main/tests/test_app)

## In Development

It's important to note that the RestiPy is under development.
