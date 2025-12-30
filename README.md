# To-Do List - Task Management Web Application

A modern, full-featured task management system built with Django 5.2, featuring project-based task organization, user authentication, and real-time HTMX interactions.

![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)
![Django Version](https://img.shields.io/badge/django-5.2-green.svg)
![Test Coverage](https://img.shields.io/badge/coverage-90.22%25-brightgreen.svg)
![Code Style](https://img.shields.io/badge/code%20style-ruff-black.svg)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Development](#development)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)

## ✨ Features

### Core Functionality
- **Project Management**: Create, update, and delete projects to organize tasks
- **Task Management**: Full CRUD operations for tasks with rich metadata
- **Task Prioritization**: Three-level priority system (Low, Medium, High)
- **Deadlines**: Optional deadline tracking with validation (cannot be in the past)
- **Task Assignment**: Assign tasks to specific users
- **Task Completion**: Toggle task completion status
- **User Authentication**: Secure login/signup with email verification via django-allauth
- **HTMX Integration**: Dynamic, SPA-like experience without full page reloads
- **Responsive Design**: Mobile-friendly interface

### Security Features
- User-based data isolation (users can only see their own projects/tasks)
- Django's built-in CSRF protection
- Secure password hashing
- Environment-based configuration
- Required SECRET_KEY validation
- ALLOWED_HOSTS configuration

### Developer Features
- Docker-compose setup for easy deployment
- Comprehensive test suite (90.22% coverage)
- Pre-commit hooks with Ruff for code quality
- PostgreSQL database with proper migrations
- Email testing with Mailpit
- Code refactoring with mixins (DRY principle)

## 🚀 Tech Stack

**Backend:**
- Python 3.13
- Django 5.2
- PostgreSQL 16
- django-allauth (authentication)
- django-htmx (HTMX integration)

**Frontend:**
- HTMX (dynamic interactions)
- Vanilla JavaScript
- CSS3

**DevOps:**
- Docker & Docker Compose
- PostgreSQL (Alpine)
- Mailpit (email testing)

**Development Tools:**
- Ruff (linting & formatting)
- pytest & pytest-django (testing)
- pytest-cov (coverage reporting)
- pre-commit (git hooks)

## 🏗️ Architecture

This application follows Django's MVT (Model-View-Template) pattern with a clear separation of concerns:

### App Structure

```
To_Do_List/
├── apps/                      # Django applications
│   ├── projects/             # Project management app
│   │   ├── models.py         # Project model with UUID primary keys
│   │   ├── views.py          # Class-based views with HTMX support
│   │   ├── managers.py       # Custom OwnedManager for user filtering
│   │   ├── mixins.py         # HTMXResponseMixin, ProjectQuerysetMixin
│   │   ├── forms.py          # Project forms with validation
│   │   └── urls.py           # URL routing
│   ├── tasks/                # Task management app
│   │   ├── models.py         # Task model with priorities & deadlines
│   │   ├── views.py          # Task CRUD operations
│   │   ├── mixins.py         # TaskHTMXMixin for HTMX responses
│   │   └── forms.py          # Task forms with deadline validation
│   └── users/                # User management & authentication
│       ├── models.py         # Custom User model
│       └── views.py          # Login, signup, profile views
└── config/                    # Project configuration
    ├── settings.py           # Django settings with env variables
    ├── urls.py               # Root URL configuration
    └── wsgi.py               # WSGI configuration
```

### Business Logic Location

1. **Models** (`models.py`): Core business entities
   - Data validation using Django's model validators
   - Business rules (e.g., ordering, default values)
   - Relationships between entities

2. **Managers** (`managers.py`): Query logic and data filtering
   - `OwnedManager`: Filters objects by user ownership
   - Reusable querysets for common operations

3. **Mixins** (`mixins.py`): Reusable view logic
   - `HTMXResponseMixin`: Common HTMX response handling
   - `ProjectQuerysetMixin`: Shared queryset logic for projects
   - `TaskHTMXMixin`: HTMX responses for tasks

4. **Views** (`views.py`): Request handling and user interactions
   - Authorization checks (LoginRequiredMixin)
   - HTMX response handling via mixins
   - Integration of forms and models

5. **Forms** (`forms.py`): Input validation and data cleaning
   - Field-level validation
   - Cross-field validation (e.g., deadline cannot be in the past)
   - Custom error messages

### Key Design Patterns

- **Custom Manager Pattern**: `OwnedManager` provides reusable user-scoped queries
- **Mixin Pattern**: Reusable view logic to eliminate code duplication (DRY)
- **UUID Primary Keys**: Using UUIDs for better security and distributed systems
- **Prefetch Related**: Optimized queries to prevent N+1 problems
- **Class-Based Views**: Reusable, maintainable view logic

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose installed on your system
- Git (for cloning the repository)

That's it! Docker handles Python, PostgreSQL, and all dependencies.

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd To_Do_List
   ```

2. **Build and start the containers**
   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build the Docker images
   - Start PostgreSQL database
   - Start Mailpit (email testing)
   - Run Django migrations
   - Start the development server

3. **Access the application**
   - **Web Application**: http://localhost:8000
   - **Mailpit (Email Testing)**: http://localhost:8025
   - **Database**: localhost:5432

### Running the Application

#### Standard Development Mode

```bash
# Start all services
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop all services
docker-compose down

# Stop and remove volumes (deletes database data)
docker-compose down -v
```

#### Creating a Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

Then access the admin panel at http://localhost:8000/admin

### Running Locally Without Docker (Alternative)

If you prefer to run without Docker:

1. **Install Python 3.13+**

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd To_Do_List
   pip install -r requirements.txt
   ```

4. **Install and start PostgreSQL**

   Create a database named `To_Do_List`

5. **Create .env file in To_Do_List/ directory**
   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   DEBUG=True
   POSTGRES_DB=To_Do_List
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ALLOWED_HOSTS=localhost,127.0.0.1
   EMAIL_HOST=localhost
   EMAIL_PORT=1025
   ```

6. **Run migrations and start server**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## 🔧 Development

### Running Tests

The project has a comprehensive test suite with 90.22% coverage.

```bash
# Run all tests with coverage report
docker-compose exec web pytest

# Run with verbose output
docker-compose exec web pytest -v

# Run specific app tests
docker-compose exec web pytest apps/projects/tests.py -v
docker-compose exec web pytest apps/tasks/tests.py -v
docker-compose exec web pytest apps/users/tests.py -v

# Generate HTML coverage report
docker-compose exec web pytest --cov=apps --cov-report=html

# View coverage report (generated in htmlcov/)
# Open htmlcov/index.html in browser
```

### Test Coverage Details

- **Models**: 8 tests covering Project, Task, and User models
- **Views**: 16 tests for CRUD operations and user isolation
- **Forms**: 6 tests for validation logic
- **Authentication**: 4 tests for login/signup flows

### Code Quality

This project uses Ruff for linting and formatting, with pre-commit hooks to ensure code quality.

#### Pre-commit Setup

```bash
# Install pre-commit hooks
docker-compose exec web pre-commit install

# Run manually on all files
docker-compose exec web pre-commit run --all-files
```

#### Manual Linting

```bash
# Check code quality
docker-compose exec web ruff check .

# Auto-fix issues
docker-compose exec web ruff check --fix .

# Format code
docker-compose exec web ruff format .
```

#### Code Style Rules

- Line length: 100 characters
- Python version: 3.13
- Import sorting: isort
- Enabled rules: pycodestyle, pyflakes, flake8-django, flake8-bugbear
- Auto-formatting with double quotes

### Database Migrations

```bash
# Create new migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Show migration status
docker-compose exec web python manage.py showmigrations
```

### Django Shell

```bash
# Open Django shell
docker-compose exec web python manage.py shell

# Example: Create a project
>>> from apps.projects.models import Project
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.first()
>>> Project.objects.create(owner=user, name="My Project", description="Test")
```

## 📁 Project Structure

```
To_Do_List/
├── docker-compose.yml           # Docker services configuration
├── pyproject.toml              # Ruff and pytest configuration
├── SQL.md                       # SQL queries documentation
├── README.md                    # This file
│
└── To_Do_List/                 # Django project directory
    ├── Dockerfile              # Docker image definition
    ├── requirements.txt        # Python dependencies
    ├── manage.py              # Django management script
    ├── pytest.ini             # Pytest configuration
    ├── conftest.py            # Pytest fixtures
    │
    ├── apps/                  # Django applications
    │   ├── projects/         # Project management
    │   │   ├── models.py     # Project model (UUID, owner, timestamps)
    │   │   ├── views.py      # CRUD views with HTMX
    │   │   ├── forms.py      # ProjectForm with validation
    │   │   ├── managers.py   # OwnedManager for user filtering
    │   │   ├── mixins.py     # HTMXResponseMixin, ProjectQuerysetMixin
    │   │   ├── urls.py       # URL patterns
    │   │   ├── admin.py      # Admin interface
    │   │   ├── tests.py      # Unit tests
    │   │   └── templates/    # Project templates
    │   │
    │   ├── tasks/            # Task management
    │   │   ├── models.py     # Task model (priority, deadline, status)
    │   │   ├── views.py      # Task CRUD with inline editing
    │   │   ├── forms.py      # TaskForm with deadline validation
    │   │   ├── mixins.py     # TaskHTMXMixin for HTMX responses
    │   │   ├── urls.py       # Task URL patterns
    │   │   ├── tests.py      # Task tests
    │   │   └── templates/    # Task templates
    │   │
    │   └── users/            # User management & auth
    │       ├── models.py     # Custom User model
    │       ├── views.py      # Auth views
    │       ├── admin.py      # User admin
    │       ├── tests.py      # User tests
    │       └── templates/    # Auth templates
    │
    ├── config/               # Django configuration
    │   ├── settings.py       # Project settings
    │   ├── urls.py           # Root URL configuration
    │   ├── wsgi.py           # WSGI entry point
    │   └── asgi.py           # ASGI entry point
    │
    ├── static/               # Static files (CSS, JS)
    │   ├── css/
    │   └── js/
    │
    ├── templates/            # Global templates
    │   ├── base.html        # Base template
    │   └── home.html        # Homepage
    │
    └── htmlcov/             # Test coverage reports
```

## 🔗 API Endpoints

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects/` | List all user's projects |
| GET | `/projects/all/` | HTMX partial: All projects with tasks |
| GET | `/projects/partial/` | HTMX partial: Projects sidebar |
| GET | `/projects/<uuid:pk>/` | Project detail with tasks |
| POST | `/projects/create/` | Create new project |
| POST | `/projects/<uuid:pk>/update/` | Update project |
| DELETE | `/projects/<uuid:pk>/delete/` | Delete project |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks/<uuid:project_pk>/create/` | Create task in project |
| POST | `/tasks/<uuid:pk>/update/` | Update task |
| DELETE | `/tasks/<uuid:pk>/delete/` | Delete task |
| POST | `/tasks/<uuid:pk>/toggle/` | Toggle task completion |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/accounts/login/` | User login |
| GET/POST | `/accounts/signup/` | User registration |
| POST | `/accounts/logout/` | User logout |
| GET | `/users/profile/` | User profile |

## ⚙️ Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_SECRET_KEY` | Django secret key | - | **Yes** (raises error if not set) |
| `DEBUG` | Debug mode | `False` | No |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `[]` | No (recommended for production) |
| `POSTGRES_DB` | PostgreSQL database name | - | Yes (for Docker) |
| `POSTGRES_USER` | PostgreSQL username | - | Yes (for Docker) |
| `POSTGRES_PASSWORD` | PostgreSQL password | - | Yes (for Docker) |
| `POSTGRES_HOST` | PostgreSQL host | `db` | Yes (for Docker) |
| `POSTGRES_PORT` | PostgreSQL port | `5432` | No |
| `EMAIL_HOST` | SMTP host | `mailpit` | No |
| `EMAIL_PORT` | SMTP port | `1025` | No |
| `USE_SQLITE_FOR_TESTS` | Use SQLite for tests | `False` | No |

**Note**: In Docker, these are configured in `docker-compose.yml`. For local development, create a `.env` file in the `To_Do_List/` directory.

## 📝 Contributing

### Git Commit Guidelines

This project follows [semantic commit messages](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: bug fix
docs: documentation changes
style: formatting, missing semicolons, etc.
refactor: code restructuring
test: adding tests
chore: maintenance tasks
```

**Examples:**
```bash
git commit -m "feat: add task priority filtering"
git commit -m "fix: resolve deadline validation issue"
git commit -m "docs: update installation instructions"
git commit -m "test: add project deletion tests"
git commit -m "refactor: add mixins to eliminate code duplication"
```

### Development Workflow

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Make changes with semantic commits
3. Run tests: `docker-compose exec web pytest`
4. Run linting: `docker-compose exec web ruff check .`
5. Push and create Pull Request

### Code Quality Standards

- All code must pass Ruff linting
- Tests should maintain >90% coverage
- Use type hints where appropriate
- Follow DRY principle (Don't Repeat Yourself)
- Use mixins for reusable view logic
- Document complex business logic

## 📚 Additional Documentation

- **SQL.md**: SQL queries and database examples

## 🔒 Security Notes

- **SECRET_KEY**: Must be set via environment variable. Application will raise an error if not provided.
- **ALLOWED_HOSTS**: Should be configured for production deployments
- **DEBUG**: Should be `False` in production
- User data is isolated by ownership - users can only access their own projects and tasks
