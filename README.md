# RestCraft WSGI Framework

RestCraft is a lightweight WSGI framework for Python, following the principles of minimalist design. It provides a solid foundation for developing web applications.

## Framework Structure

RestCraft is divided into two main parts:

- **Framework:** Provides the tools, libraries, and base structures needed for web application development. This includes mechanisms for routing requests, handling responses, and a robust middleware system.

- **Project:** The specific application created by the developer using the framework. Here, the developer can define routes, views, middlewares, and any other application-specific logic.

## Main Features

### Settings

- **Configuration File:** Centralizes project settings, allowing the definition of directories for dependencies such as views and middleware folders.

### Middlewares

- **Early Return:** Allows for the early interruption and return of a request before reaching the final handler.
- **Request/Response Modification:** Facilitates the alteration of response and request objects at any stage of the process.
- **Lifecycle Methods:**
  - **before_route:** Executed before a route handler, useful for preprocessing logic.
  - **before_handler:** Executed after route matching and before the handler, ideal for validations and authorizations.
  - **after_handler:** Invoked after the route handler's execution, allowing for modification of the response before it is sent to the client.

### Views

- **Classes:** Uses a class-based system to define views, providing an organized and reusable structure.
- **Defines Routes:** Allows for the explicit definition of routes within view classes.
- **Lifecycle Methods:**
  - **before_handler:** Executed before the handler.
  - **handler:** Route handler where the main logic of the request is processed.
  - **after_handler:** Executed after the handler.
  - **on_exception:** Executed if an exception occurs during the handling of a request.
- **Route Attributes:**
  - **route:** The route pattern.
  - **methods:** List of HTTP methods supported by this route (e.g., GET, POST).

### Routes

- **Dynamic Routing:** RestCraft allows you to specify parts of the URL to be dynamic. These dynamic segments can capture parts of the URL as variables, which can then be passed to your request handlers. For example, defining a route like "/user/<username>" can capture any username and pass it to the handler.
- **Wildcard Filters:** You can use wildcard filters in the routes to capture data with specific formats. For instance, you can define a route to only accept integers int or str, uuid and slug. This lets you tailor the handler functions to specific data types or patterns, improving flexibility and reducing the need for validating URLs within your handlers.

### Exceptions

- **Easy Custom Exceptions:** Framework supports of custom exceptions, which can be integrated into the application's error handling strategy easily.

### Project Example

Explore a sample project using RestCraft to see how everything comes together: [Manganato API](https://github.com/lsfratel/manganatoapi)

## In Development

It's important to note that RestCraft is under development. Features and functionality may change as the framework evolves.
