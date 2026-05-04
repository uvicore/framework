# Uvicore Framework - Public API Summary

## Overview
This document outlines the public APIs and testable functionality for the 8 key uvicore modules. Each module provides specific functionality for building async web applications, CLI tools, and data processing systems.

---

## 1. HTTP Module (FastAPI routing and request handling)

**Location:** `uvicore/http/`

### Core Components

#### Request Class
- **Import:** `from uvicore.http import Request`
- **Description:** Extended Starlette Request object for HTTP request handling
- **Module:** `uvicore.http.request.Request`
- **Key Aspects:**
  - Wraps Starlette's Request for enhanced functionality
  - Accessible in all HTTP route handlers
  - Provides access to query parameters, body, headers, cookies, etc.

#### Response Namespace
- **Import:** `from uvicore.http import response` (as namespace)
- **Available Response Types:**
  - `response.View()` - Jinja2 template responses with view composers
  - `response.File()` - File download responses
  - `response.HTML()` - HTML responses
  - `response.JSON()` / `response.UJSON()` / `response.ORJSON()` - JSON responses
  - `response.Text()` - Plain text responses
  - `response.Redirect()` - Redirect responses
  - `response.Stream()` - Streaming responses

#### Request Parameters
- **Import:** `from uvicore.http import Parameter`
- **FastAPI Params:** `Path`, `Query`, `Header`, `Cookie`, `Body`, `Form`, `File`, `Depends`, `Security`
- **Description:** Custom parameter handling with infinite kwargs support for advanced routing

### Routing System

#### Router Classes
- **Import:** `from uvicore.http.routing import (ApiRouter, ApiRoute, WebRouter, WebRoute, Router, Routes, Controller, Guard)`

**Router Types:**
1. **WebRouter** - Traditional web routes with template rendering
   - Methods: `.get()`, `.post()`, `.put()`, `.patch()`, `.delete()`, `.head()`, `.options()`
   - Returns decorator or accepts endpoint callable
   - Parameters:
     - `path` - URL path
     - `endpoint` - Handler function
     - `name` - Route name for URL generation
     - `autoprefix` - Enable route name prefixing
     - `middleware` - Route-level middleware list
     - `auth` - Guard/authentication requirement
     - `scopes` - Permission scopes

2. **ApiRouter** - RESTful API routes with OpenAPI documentation
   - Same HTTP methods as WebRouter
   - Additional Parameters:
     - `response_model` - Pydantic model for response
     - `response_class` - Custom response class
     - `tags` - OpenAPI tags for documentation
     - `summary` - Endpoint summary for docs
     - `description` - Endpoint description for docs
     - `responses` - Response status codes dictionary
     - `inherits` - Parameter inheritance from other endpoints

3. **Routes/Controller** - Controller class for organizing routes
   - `register(router)` method - Register routes on a router
   - `_middleware()` method - Controller-level middleware

#### Router Methods
- `.controller(module, prefix='', name='', tags=None, options={})`
- `.include(module, prefix='', name='', tags=None, options={})` (alias to controller)
- `.group(prefix='', routes=None, name='', tags=None, autoprefix=True, middleware=None, auth=None, scopes=None)`

#### Guard Class
- **Import:** `from uvicore.http.routing import Guard`
- **Description:** Authentication and permission scoping
- **Usage:** `Guard(['permission1', 'permission2'])`

### HTTP Exceptions

**Import:** `from uvicore.http.exceptions import (...)`

**Exception Classes:**
- `HTTPException(status_code, detail=None, message=None, exception=None, extra=None, headers=None)` - Base exception
- `PermissionDenied(permissions=None, detail=None, extra=None, headers=None)` - 401 Unauthorized
- `NotAuthenticated(detail=None, extra=None, headers=None)` - 401 Unauthorized
- `InvalidCredentials(detail=None, extra=None, headers=None)` - 401 Unauthorized
- `NotFound(detail=None, extra=None, headers=None)` - 404 Not Found
- `BadParameter(detail=None, exception=None, extra=None, headers=None)` - 400 Bad Request

**Properties:**
- `status_code` - HTTP status code
- `message` - User-friendly message (shows HTTP status phrase or custom)
- `detail` - Detailed error description
- `exception` - Stack trace (shown only in debug mode)
- `extra` - Additional error context (dict)
- `headers` - Custom HTTP headers

### HTTP Status Codes
**Import:** `from uvicore.http import status`
- `HTTP_200_OK`, `HTTP_201_CREATED`, `HTTP_204_NO_CONTENT`
- `HTTP_400_BAD_REQUEST`, `HTTP_401_UNAUTHORIZED`, `HTTP_403_FORBIDDEN`
- `HTTP_404_NOT_FOUND`, `HTTP_500_INTERNAL_SERVER_ERROR`, etc.

---

## 2. Console Module (CLI commands using Async Click)

**Location:** `uvicore/console/`

### Core Components

#### Command Decorator
- **Import:** `from uvicore.console import command`
- **Description:** Decorated with custom colored help text
- **Usage:** `@command(name='command_name')`
- **Features:**
  - Colored help headers (yellow)
  - Colored help options (green)
  - Returns `HelpColorsCommand` with customization

#### Group Decorator
- **Import:** `from uvicore.console import group`
- **Description:** Creates command groups for organizing CLI commands
- **Usage:** `@group(name='group_name')`
- **Features:**
  - Colored help headers (yellow)
  - Colored help options (green)
  - Returns `HelpColorsGroup` with customization

#### Click Parameters
- **Import:** `from uvicore.console import argument, option`
- **Description:** AsyncClick parameter decorators
- **Functions:**
  - `@argument(name, required=True, nargs=-1, etc.)`
  - `@option(name, '--flag', '-f', help='description', etc.)`
  - Both support async callbacks and validations

#### AsyncClick Library
- **Import:** `from uvicore.console import asyncclick as click`
- **Description:** Local copy of asyncclick for async command support
- **Features:** Full asyncclick API with async/await support

#### Utility Function
- **Function:** `command_is(command: str) -> bool`
- **Description:** Check if a specific command is currently running
- **Usage:** `if uvicore.console.command_is('migrate'):`

### Command Structure
```python
@command()
@argument('name')
@option('--help', '-h', is_flag=True)
async def my_command(name: str, help: bool):
    """Command docstring"""
    pass
```

---

## 3. Templating Module (Jinja2 template rendering)

**Location:** `uvicore/templating/`

### Core Components

#### Templates Class
- **Import:** `from uvicore.templating.engine import Templates`
- **Service Name:** `'uvicore.templating.engine.Templates'`
- **Aliases:** `'Templates'`, `'templates'`
- **Singleton:** Yes

**Properties:**
- `env` - Jinja2 Environment instance
- `paths` - List of template directories
- `context_functions` - Global Jinja2 functions (dict)
- `context_filters` - Global Jinja2 filters (dict)
- `filters` - Custom filters (dict)
- `tests` - Custom tests (dict)

**Public Methods:**

1. **render(template_name: str, data: dict = {}) -> str**
   - Renders template as string
   - Used primarily for CLI templating
   - Returns rendered template string

2. **render_web_response(name: str, context: dict, status_code: int = 200, headers: dict = None, media_type: str = None, background: BackgroundTask = None)**
   - Renders template as Starlette web response
   - Requires `'request'` key in context
   - Returns `_TemplateResponse` object
   - Parameters:
     - `name` - Template file name
     - `context` - Template context dict (must include request)
     - `status_code` - HTTP status code
     - `headers` - Custom HTTP headers
     - `media_type` - Content type override
     - `background` - Background task to run after response

### Jinja2 Features
- **Engine Features:**
  - Loader: FileSystemLoader with configurable paths
  - Autoescape: Enabled for HTML safety
  - Keep trailing newlines: True
  - Template inheritance and includes
  - Custom filters and tests
  - Context processors for dynamic data

### Configuration
- Template paths configured in app config
- View composers for dynamic template context
- Filter registration for custom transformations
- Test definitions for template logic

---

## 4. Exceptions Module (Smart exception handling)

**Location:** `uvicore/exceptions/exceptions.py`

### Core Components

#### SmartException Class
- **Attributes:**
  - `detail` - Detailed error message
  - `status_code` - HTTP/exit status (default: 500 for HTTP, 1 for CLI)
  - `message` - User-friendly message (default: 'An error has occured')
  - `exception` - Stack trace (shown only in debug mode)
  - `extra` - Additional context dict
  - `headers` - HTTP response headers (HTTP only)

**Constructor:**
```python
SmartException(
    detail: str,
    status_code: int = None,
    message: str = None,
    exception: str = None,
    extra: dict = None,
    headers: dict = None
)
```

### Smart Behavior
- **Dual-Mode Operation:**
  - When used in HTTP context (uvicore.app.is_http=True):
    - Inherits from HTTPException
    - Uses HTTP status codes (500 default)
    - Includes headers support
  - When used in CLI context (non-HTTP):
    - Standalone exception
    - Uses exit codes (1 default for general errors)
    - No headers needed

**Configuration Dependency:**
- `uvicore.config.app.debug` - Controls visibility of exception stack traces
- Stack traces hidden in production unless debug=True

---

## 5. Mail Module (Email functionality)

**Location:** `uvicore/mail/mail.py`

### Core Components

#### Mail Class
- **Service Name:** Decorated with `@uvicore.service()`
- **Decorator-enabled singleton service**

**Constructor Parameters:**
```python
Mail(
    mailer: str = None,              # Mailer driver name
    mailer_options: dict = None,     # Driver-specific options
    to: list = [],                   # Recipients
    cc: list = [],                   # Carbon copy recipients
    bcc: list = [],                  # Blind carbon copy
    from_name: str = None,           # Sender name
    from_address: str = None,        # Sender email address
    subject: str = None,             # Email subject
    html: str = None,                # HTML body
    text: str = None,                # Plain text body
    attachments: list = []           # File attachments
)
```

**Public Methods (all chainable):**
- `mailer(mailer: str) -> Mail` - Switch mailer driver
- `mailer_options(options: dict) -> Mail` - Set driver options
- `to(to: list) -> Mail` - Set recipients
- `cc(cc: list) -> Mail` - Set CC recipients
- `bcc(bcc: list) -> Mail` - Set BCC recipients
- `from_name(from_name: str) -> Mail` - Set sender name
- `from_address(from_address: str) -> Mail` - Set sender email
- `subject(subject: str) -> Mail` - Set email subject
- `html(html: str) -> Mail` - Set HTML body
- `text(text: str) -> Mail` - Set text body
- `attachments(attachments: list) -> Mail` - Set attachments
- `async send()` - Send the email

**Configuration:**
- Default mailer from `uvicore.config.app.mail.default`
- Mailer options from `uvicore.config.app.mail.mailers[mailer_name]`
- From name from `uvicore.config.app.mail.from_name`
- From address from `uvicore.config.app.mail.from_address`

**Mailer Types:**
- Driver specified in `mailer_options.driver`
- Dynamically loaded at send time
- Examples: SMTP, SendGrid, Mailgun, etc.

**Email Contract:**
- Message stored as `uvicore.contracts.Email` SuperDict
- Properties: `to`, `cc`, `bcc`, `from_name`, `from_address`, `subject`, `html`, `text`, `attachments`

---

## 6. Redis Module (Redis integration)

**Location:** `uvicore/redis/redis.py`

### Core Components

#### Redis Class
- **Service Name:** `'uvicore.redis.redis.Redis'`
- **Aliases:** `'Redis'`, `'redis'`
- **Singleton:** Yes

**Properties:**
- `default` - Default connection name (string)
- `connections` - Dict of connection configuration objects
- `engines` - Dict of active redis.asyncio connection pools

**Public Methods:**

1. **init(default: str, connections: dict[str, object])**
   - Initialize Redis with connections
   - Builds connection URLs from host/port/database/password
   - Called during bootstrap

2. **connection(connection: str = None) -> object**
   - Get connection configuration by name
   - Returns connection config object with properties:
     - `host` - Server hostname
     - `port` - Server port
     - `database` - Database number
     - `password` - Authentication password (optional)
     - `url` - Full Redis connection URL
   - Raises Exception if connection not found

3. **async connect(connection: str = None) -> redis.Redis**
   - Establish or return connection pool
   - Creates connection pool if not yet created
   - Caches pools by connection URL
   - Returns active redis.asyncio.Redis instance

### Connection Management
- **Lazy Connection:** Pools created on first access
- **Connection Pooling:** Single pool per unique URL
- **URL Format:** `redis://[host]:[port]/[database]?password=[password]`

### Redis CLI Commands
- Full aioredis async command support available through returned connection
- See https://aioredis.readthedocs.io/en/latest/mixins.html#generic-commands
- Common commands: GET, SET, DEL, HGET, LPUSH, ZADD, EXPIRE, etc.

---

## 7. Logging Module (Logging system)

**Location:** `uvicore/logging/logger.py`

### Core Components

#### ColoredFormatter Class
- **Description:** Custom logging formatter with colored output
- **Inheritance:** Extends standard `logging.Formatter`
- **Constructor:** `ColoredFormatter(pattern)`
- **Output:** Console-only formatting (not for file handlers)

**Colored Format Support:**
- **Headers:** `:: text ::` (dark orange + green)
- **Headers 2:** `## text ##` (dark orange + green)
- **Headers 3:** `=== text ===` (dark orange + green)
- **Headers 4:** `---- text ----` (dark orange + dark green)
- **Bullet lists:** `* item` (green bullet + white text)
- **Error markers:** `- error` (red marker + white text)
- **Positive markers:** `+ success` (cyan marker + white text)
- **Notice markers:** `> notice` (magenta marker + white text)
- **NOTICE prefix:** `NOTICE: text` (yellow bold + white bold)

#### OutputFilter Class
- **Description:** Python logging filter with inclusion/exclusion lists
- **Constructor:** `OutputFilter(filters, excludes)`
- **Behavior:**
  - Prefix matching on logger names
  - Includes: Shows all if empty list, otherwise shows only matching
  - Excludes: Hides matching loggers regardless of includes
  - Matching: `A.B` matches `A.B`, `A.B.C`, `A.B.C.D`, etc.

#### ExcludeFilter Class
- **Description:** Opposite of OutputFilter - only excludes
- **Constructor:** `ExcludeFilter(excludes)`
- **Behavior:** Hides all matching loggers by prefix

#### Logger Class (PythonLogger)
- **Import:** `logging.Logger` (Python standard library)
- **Configured through:** Django-style logging configuration
- **Methods:** `debug()`, `info()`, `warning()`, `error()`, `critical()`

### Configuration Options
- Logger names with hierarchical filtering
- Multiple handlers (console, file, syslog, etc.)
- Custom formatters and filters
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Propagation control

---

## 8. Auth Module (Authentication system)

**Location:** `uvicore/auth/`

### Core Components

#### Auth Class
- **Service Name:** Aliased as `'Auth'`, `'auth'`
- **Location:** `uvicore/auth/auth.py`
- **Current Status:** Placeholder service (minimal implementation)
- **Purpose:** Central authentication service

#### UserInfo Class
- **Service Name:** Decorated with `@uvicore.service()`
- **Location:** `uvicore/auth/user_info.py`
- **Inheritance:** Extends `pydantic.BaseModel` and `UserInfoInterface`
- **Use Case:** Represents authenticated user information

**Properties (as Pydantic fields):**
- `id` - User ID (int)
- `uuid` - User UUID (str)
- `username` - Username (str)
- `email` - Email address (str)
- `first_name` - First name (str)
- `last_name` - Last name (str)
- `title` - User title (optional str)
- `avatar` - Avatar URL (optional str)
- `groups` - List of group names (list[str])
- `roles` - List of role names (list[str])
- `permissions` - List of permission strings (list[str])
- `superadmin` - Is superadmin flag (bool)
- `authenticated` - Is logged in flag (bool)
- `extra` - Additional custom data (optional dict)

**Computed Properties:**
- `name` -> `first_name + last_name`
- `avatar_url` -> alias to `avatar`
- `admin` -> `superadmin`
- `is_admin` -> `superadmin`
- `is_superadmin` -> `superadmin`
- `is_not_admin` -> `not superadmin`
- `is_authenticated` -> `authenticated`
- `loggedin` -> `authenticated`
- `is_loggedin` -> `authenticated`
- `is_not_loggedin` -> `not authenticated`
- `is_not_authenticated` -> `not authenticated`
- `check` -> `authenticated`

**Public Methods:**

1. **can(permissions: Union[str, List]) -> bool**
   - Check if user has ALL specified permissions
   - Returns True if user is superadmin (bypass check)
   - Accepts: Single permission string or list of permission strings
   - Returns: True if user has all permissions, False otherwise

### Module Structure
- `uvicore/auth/auth.py` - Auth service
- `uvicore/auth/user_info.py` - UserInfo model
- `uvicore/auth/authenticators/` - Authentication drivers
- `uvicore/auth/user_providers/` - User data providers
- `uvicore/auth/http/` - HTTP middleware and decorators
- `uvicore/auth/models/` - Database ORM models
- `uvicore/auth/database/` - Database utilities
- `uvicore/auth/config/` - Configuration files
- `uvicore/auth/commands/` - CLI commands for auth management

### Authentication Flow
1. **User Provider:** Loads user data via `user_providers`
2. **Authenticator:** Validates credentials via `authenticators`
3. **UserInfo:** Represents logged-in user state
4. **Middleware:** Applies authentication to HTTP requests
5. **Guard:** Enforces permission scopes on routes

### Middleware Integration
- HTTP middleware for automatic user loading
- Request-scoped user information injection
- OpenAPI/Swagger security scheme support

---

## Cross-Module Dependencies

### Service Container (IoC)
All modules can be accessed through:
```python
import uvicore

# Access services
templates = uvicore.ioc.make('Templates')
redis = uvicore.ioc.make('Redis')
mail = uvicore.ioc.make('Mail')
auth = uvicore.ioc.make('Auth')
```

### Configuration Access
All modules use centralized configuration:
```python
uvicore.config.app.mail            # Mail configuration
uvicore.config.app.debug           # Debug mode for exception display
uvicore.config.uvicore.http        # HTTP configuration
uvicore.config.uvicore.database    # Database configuration
```

### Common Patterns

**Singleton Services:**
- Templates
- Redis
- Mail
- Logger

**Interfaces (Contracts):**
- `uvicore.contracts.Email`
- `uvicore.contracts.Template`
- `uvicore.contracts.Logger`
- `uvicore.contracts.Router`
- `uvicore.contracts.UserInfo`

**SuperDict Utility:**
- Used for flexible configuration objects
- Chainable method returns (fluent interface)
- Merge, clone, and data manipulation methods

---

## Testing Recommendations

### 1. HTTP Module Tests
- Route registration and naming
- Request parameter parsing
- Response type rendering
- Exception handling and status codes
- View composer integration
- Guard/authentication enforcement

### 2. Console Module Tests
- Command registration and execution
- Async command execution
- Argument and option parsing
- Help text generation
- Command detection with `command_is()`

### 3. Templating Module Tests
- Template rendering for CLI and web
- Context data passing
- Jinja2 filter and test registration
- Template inheritance and includes
- Background task execution with responses

### 4. Exceptions Module Tests
- HTTP vs CLI exception behavior
- Status code determination
- Message and detail handling
- Debug mode stack trace display
- Exception chaining and extra context

### 5. Mail Module Tests
- Mailer initialization
- Message builder chainability
- Recipient and sender setup
- Attachment handling
- Driver selection and options
- Email sending execution

### 6. Redis Module Tests
- Connection configuration
- Pool creation and reuse
- Connection retrieval
- Async operations
- URL building with authentication
- Multiple connection management

### 7. Logging Module Tests
- ColoredFormatter output
- Filter inclusion/exclusion logic
- Logger name prefix matching
- Custom format string application
- Colored output validation

### 8. Auth Module Tests
- UserInfo model validation
- Permission checking
- Role and group membership
- Superadmin bypass behavior
- User property aliases
- Extra data handling

