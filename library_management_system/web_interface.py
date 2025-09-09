"""Web interface for the Library Management System with theming support."""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
    from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from fastapi.security import HTTPBearer
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from .auth import AuthManager, User, Role, Permission
from .library import Library
from .secure_data_manager import SecureDataManager
from .enhanced_search import EnhancedSearch
from .i18n import get_i18n, t
from .models import Book, Member


class ThemeManager:
    """Manages themes for the web interface."""
    
    def __init__(self, themes_dir: str = "static/themes"):
        """Initialize theme manager.
        
        Args:
            themes_dir: Directory containing theme files
        """
        self.themes_dir = Path(themes_dir)
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        self.themes = {}
        self.current_theme = "light"
        
        self._create_default_themes()
        self._load_themes()
    
    def _create_default_themes(self) -> None:
        """Create default themes."""
        # Light theme
        light_theme = {
            "name": "Light",
            "key": "light",
            "colors": {
                "primary": "#007bff",
                "secondary": "#6c757d",
                "success": "#28a745",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "info": "#17a2b8",
                "light": "#f8f9fa",
                "dark": "#343a40",
                "background": "#ffffff",
                "surface": "#f8f9fa",
                "text_primary": "#212529",
                "text_secondary": "#6c757d",
                "border": "#dee2e6",
                "shadow": "rgba(0, 0, 0, 0.125)",
            },
            "typography": {
                "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                "font_size_base": "1rem",
                "line_height_base": "1.5",
                "heading_font_weight": "600",
            },
            "spacing": {
                "base": "1rem",
                "small": "0.5rem",
                "large": "1.5rem",
                "xlarge": "3rem",
            },
            "borders": {
                "radius": "0.375rem",
                "width": "1px",
            }
        }
        
        # Dark theme
        dark_theme = {
            "name": "Dark",
            "key": "dark",
            "colors": {
                "primary": "#0d6efd",
                "secondary": "#6c757d",
                "success": "#198754",
                "danger": "#dc3545",
                "warning": "#fd7e14",
                "info": "#0dcaf0",
                "light": "#f8f9fa",
                "dark": "#212529",
                "background": "#121212",
                "surface": "#1e1e1e",
                "text_primary": "#ffffff",
                "text_secondary": "#adb5bd",
                "border": "#495057",
                "shadow": "rgba(0, 0, 0, 0.3)",
            },
            "typography": {
                "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                "font_size_base": "1rem",
                "line_height_base": "1.5",
                "heading_font_weight": "600",
            },
            "spacing": {
                "base": "1rem",
                "small": "0.5rem",
                "large": "1.5rem",
                "xlarge": "3rem",
            },
            "borders": {
                "radius": "0.375rem",
                "width": "1px",
            }
        }
        
        # High contrast theme for accessibility
        high_contrast_theme = {
            "name": "High Contrast",
            "key": "high_contrast",
            "colors": {
                "primary": "#000000",
                "secondary": "#666666",
                "success": "#008000",
                "danger": "#ff0000",
                "warning": "#ff8000",
                "info": "#0000ff",
                "light": "#ffffff",
                "dark": "#000000",
                "background": "#ffffff",
                "surface": "#ffffff",
                "text_primary": "#000000",
                "text_secondary": "#333333",
                "border": "#000000",
                "shadow": "rgba(0, 0, 0, 0.5)",
            },
            "typography": {
                "font_family": "Arial, sans-serif",
                "font_size_base": "1.125rem",
                "line_height_base": "1.6",
                "heading_font_weight": "bold",
            },
            "spacing": {
                "base": "1.25rem",
                "small": "0.625rem",
                "large": "1.875rem",
                "xlarge": "3.75rem",
            },
            "borders": {
                "radius": "0",
                "width": "2px",
            }
        }
        
        self.themes = {
            "light": light_theme,
            "dark": dark_theme,
            "high_contrast": high_contrast_theme,
        }
    
    def _load_themes(self) -> None:
        """Load themes from files."""
        # In a real implementation, you might load custom themes from files
        pass
    
    def get_theme(self, theme_key: str) -> Dict[str, Any]:
        """Get a theme by key.
        
        Args:
            theme_key: Theme key
            
        Returns:
            Theme dictionary
        """
        return self.themes.get(theme_key, self.themes["light"])
    
    def get_available_themes(self) -> List[Dict[str, str]]:
        """Get list of available themes.
        
        Returns:
            List of theme info dictionaries
        """
        return [
            {"key": key, "name": theme["name"]}
            for key, theme in self.themes.items()
        ]
    
    def set_current_theme(self, theme_key: str) -> bool:
        """Set the current theme.
        
        Args:
            theme_key: Theme key to set
            
        Returns:
            True if theme was set, False if theme not found
        """
        if theme_key in self.themes:
            self.current_theme = theme_key
            return True
        return False
    
    def get_css_variables(self, theme_key: Optional[str] = None) -> str:
        """Get CSS variables for a theme.
        
        Args:
            theme_key: Theme key (uses current theme if None)
            
        Returns:
            CSS variable declarations
        """
        theme = self.get_theme(theme_key or self.current_theme)
        
        css_vars = [":root {"]
        
        # Add color variables
        for name, value in theme["colors"].items():
            css_vars.append(f"  --color-{name.replace('_', '-')}: {value};")
        
        # Add typography variables
        for name, value in theme["typography"].items():
            css_vars.append(f"  --{name.replace('_', '-')}: {value};")
        
        # Add spacing variables
        for name, value in theme["spacing"].items():
            css_vars.append(f"  --spacing-{name}: {value};")
        
        # Add border variables
        for name, value in theme["borders"].items():
            css_vars.append(f"  --border-{name.replace('_', '-')}: {value};")
        
        css_vars.append("}")
        
        return "\n".join(css_vars)


class WebInterface:
    """Web interface for the Library Management System."""
    
    def __init__(
        self,
        library: Optional[Library] = None,
        auth_manager: Optional[AuthManager] = None,
        theme_manager: Optional[ThemeManager] = None,
        templates_dir: str = "templates",
        static_dir: str = "static",
    ):
        """Initialize web interface.
        
        Args:
            library: Library instance
            auth_manager: Authentication manager
            theme_manager: Theme manager
            templates_dir: Templates directory
            static_dir: Static files directory
        """
        if not HAS_FASTAPI:
            raise ImportError("FastAPI is required for web interface")
        
        self.app = FastAPI(
            title="Library Management System",
            description="Web interface for library management",
            version="1.0.0",
        )
        
        # Initialize components
        data_manager = SecureDataManager(enable_encryption=True, enable_backups=True)
        self.library = library or Library(data_manager)
        self.auth_manager = auth_manager or AuthManager()
        self.theme_manager = theme_manager or ThemeManager()
        self.enhanced_search = EnhancedSearch()
        self.i18n = get_i18n()
        
        # Setup directories
        self.templates_dir = Path(templates_dir)
        self.static_dir = Path(static_dir)
        self.templates_dir.mkdir(exist_ok=True)
        self.static_dir.mkdir(exist_ok=True)
        
        # Setup templates
        self.templates = Jinja2Templates(directory=str(self.templates_dir))
        
        # Setup static files
        self.app.mount("/static", StaticFiles(directory=str(self.static_dir)), name="static")
        
        # Security
        self.security = HTTPBearer(auto_error=False)
        
        # Create default templates
        self._create_default_templates()
        
        # Setup routes
        self._setup_routes()
        
        # Update search index
        self.enhanced_search.update_index(self.library.display_books(), self.library.display_members())
    
    def _create_default_templates(self) -> None:
        """Create default HTML templates."""
        # Base template
        base_template = '''<!DOCTYPE html>
<html lang="{{ language }}" data-theme="{{ theme }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ t('welcome') }}{% endblock %} - Library Management System</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    <!-- Custom theme CSS -->
    <style>
        {{ theme_css | safe }}
        
        /* Theme-aware styles */
        body {
            background-color: var(--color-background);
            color: var(--color-text-primary);
            font-family: var(--font-family);
            font-size: var(--font-size-base);
            line-height: var(--line-height-base);
        }
        
        .navbar {
            background-color: var(--color-primary) !important;
        }
        
        .card {
            background-color: var(--color-surface);
            border: var(--border-width) solid var(--color-border);
            border-radius: var(--border-radius);
            box-shadow: 0 0.125rem 0.25rem var(--color-shadow);
        }
        
        .btn-primary {
            background-color: var(--color-primary);
            border-color: var(--color-primary);
        }
        
        .btn-secondary {
            background-color: var(--color-secondary);
            border-color: var(--color-secondary);
        }
        
        .table {
            --bs-table-bg: var(--color-surface);
            --bs-table-color: var(--color-text-primary);
        }
        
        .form-control, .form-select {
            background-color: var(--color-surface);
            border-color: var(--color-border);
            color: var(--color-text-primary);
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--color-primary);
            box-shadow: 0 0 0 0.2rem rgba(var(--color-primary), 0.25);
        }
        
        /* Dark mode specific adjustments */
        [data-theme="dark"] .table-striped > tbody > tr:nth-of-type(odd) > td {
            background-color: rgba(255, 255, 255, 0.05);
        }
        
        /* High contrast theme adjustments */
        [data-theme="high_contrast"] * {
            outline: var(--border-width) solid transparent;
        }
        
        [data-theme="high_contrast"] *:focus {
            outline: var(--border-width) solid var(--color-primary);
        }
        
        /* Accessibility improvements */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        
        /* Animation preferences */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-book"></i> {{ t('welcome') }}
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" 
                    aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    {% if current_user %}
                        <li class="nav-item">
                            <a class="nav-link" href="/dashboard">
                                <i class="fas fa-tachometer-alt"></i> {{ t('dashboard') }}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/books">
                                <i class="fas fa-book"></i> {{ t('books') }}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/members">
                                <i class="fas fa-users"></i> {{ t('members') }}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/search">
                                <i class="fas fa-search"></i> {{ t('search') }}
                            </a>
                        </li>
                    {% endif %}
                </ul>
                
                <ul class="navbar-nav">
                    <!-- Theme selector -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="themeDropdown" role="button" 
                           data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-palette"></i> {{ t('theme') }}
                        </a>
                        <ul class="dropdown-menu" aria-labelledby="themeDropdown">
                            {% for theme in available_themes %}
                                <li>
                                    <a class="dropdown-item theme-option" href="#" data-theme="{{ theme.key }}">
                                        {{ theme.name }}
                                    </a>
                                </li>
                            {% endfor %}
                        </ul>
                    </li>
                    
                    <!-- Language selector -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="languageDropdown" role="button" 
                           data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-globe"></i> {{ t('language') }}
                        </a>
                        <ul class="dropdown-menu" aria-labelledby="languageDropdown">
                            {% for lang in available_languages %}
                                <li>
                                    <a class="dropdown-item language-option" href="#" data-language="{{ lang }}">
                                        {{ t(lang) }}
                                    </a>
                                </li>
                            {% endfor %}
                        </ul>
                    </li>
                    
                    {% if current_user %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" 
                               data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="fas fa-user"></i> {{ current_user.username }}
                            </a>
                            <ul class="dropdown-menu" aria-labelledby="userDropdown">
                                <li><a class="dropdown-item" href="/profile">{{ t('profile') }}</a></li>
                                <li><a class="dropdown-item" href="/settings">{{ t('settings') }}</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="/logout">{{ t('logout') }}</a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="/login">{{ t('login') }}</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    
    <!-- Main content -->
    <main class="container mt-4" role="main">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    <footer class="bg-light mt-5 py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2024 Library Management System. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-end">
                    <a href="/help" class="text-decoration-none me-3">{{ t('help') }}</a>
                    <a href="/about" class="text-decoration-none">{{ t('about') }}</a>
                </div>
            </div>
        </div>
    </footer>
    
    <!-- Bootstrap JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JavaScript -->
    <script>
        // Theme switching
        document.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const theme = this.dataset.theme;
                document.documentElement.setAttribute('data-theme', theme);
                localStorage.setItem('preferred-theme', theme);
                
                // Update theme on server
                fetch('/api/set-theme', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({theme: theme})
                });
            });
        });
        
        // Language switching
        document.querySelectorAll('.language-option').forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const language = this.dataset.language;
                
                // Update language on server
                fetch('/api/set-language', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({language: language})
                }).then(() => {
                    window.location.reload();
                });
            });
        });
        
        // Load saved theme preference
        const savedTheme = localStorage.getItem('preferred-theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
        }
        
        // Keyboard navigation improvements
        document.addEventListener('keydown', function(e) {
            // Skip to main content with Alt+M
            if (e.altKey && e.key === 'm') {
                document.querySelector('main').focus();
            }
            
            // Focus search with Alt+S
            if (e.altKey && e.key === 's') {
                const searchInput = document.querySelector('input[type="search"]');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        });
    </script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>'''
        
        # Login template
        login_template = '''{% extends "base.html" %}

{% block title %}{{ t('login') }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
        <div class="card">
            <div class="card-header text-center">
                <h4><i class="fas fa-sign-in-alt"></i> {{ t('login') }}</h4>
            </div>
            <div class="card-body">
                {% if error_message %}
                    <div class="alert alert-danger" role="alert">
                        {{ error_message }}
                    </div>
                {% endif %}
                
                <form method="post" action="/login">
                    <div class="mb-3">
                        <label for="username" class="form-label">{{ t('username') }}</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="password" class="form-label">{{ t('password') }}</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-sign-in-alt"></i> {{ t('login') }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
        
        # Dashboard template
        dashboard_template = '''{% extends "base.html" %}

{% block title %}{{ t('dashboard') }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1>{{ t('dashboard') }}</h1>
        <p class="lead">{{ t('welcome') }}, {{ current_user.username }}!</p>
    </div>
</div>

<div class="row mb-4">
    <!-- Statistics cards -->
    <div class="col-md-3 mb-3">
        <div class="card text-white bg-primary">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h5 class="card-title">{{ t('total_books') }}</h5>
                        <h3>{{ stats.total_books }}</h3>
                    </div>
                    <div class="align-self-center">
                        <i class="fas fa-book fa-2x"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-3 mb-3">
        <div class="card text-white bg-success">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h5 class="card-title">{{ t('books_available') }}</h5>
                        <h3>{{ stats.available_books }}</h3>
                    </div>
                    <div class="align-self-center">
                        <i class="fas fa-check-circle fa-2x"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-3 mb-3">
        <div class="card text-white bg-info">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h5 class="card-title">{{ t('total_members') }}</h5>
                        <h3>{{ stats.total_members }}</h3>
                    </div>
                    <div class="align-self-center">
                        <i class="fas fa-users fa-2x"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-3 mb-3">
        <div class="card text-white bg-warning">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h5 class="card-title">{{ t('books_issued') }}</h5>
                        <h3>{{ stats.issued_books }}</h3>
                    </div>
                    <div class="align-self-center">
                        <i class="fas fa-hand-holding fa-2x"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <!-- Quick actions -->
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-bolt"></i> {{ t('quick_actions') }}</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="/books/add" class="btn btn-outline-primary">
                        <i class="fas fa-plus"></i> {{ t('add_book') }}
                    </a>
                    <a href="/members/add" class="btn btn-outline-success">
                        <i class="fas fa-user-plus"></i> {{ t('add_member') }}
                    </a>
                    <a href="/circulation/issue" class="btn btn-outline-info">
                        <i class="fas fa-hand-holding"></i> {{ t('issue_book') }}
                    </a>
                    <a href="/circulation/return" class="btn btn-outline-warning">
                        <i class="fas fa-undo"></i> {{ t('return_book') }}
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Recent activity -->
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-clock"></i> {{ t('recent_activity') }}</h5>
            </div>
            <div class="card-body">
                {% if recent_activities %}
                    <ul class="list-unstyled">
                        {% for activity in recent_activities %}
                            <li class="mb-2">
                                <small class="text-muted">{{ activity.timestamp }}</small><br>
                                {{ activity.description }}
                            </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p class="text-muted">{{ t('no_recent_activity') }}</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
        
        # Write templates to files
        templates = {
            "base.html": base_template,
            "login.html": login_template,
            "dashboard.html": dashboard_template,
        }
        
        for filename, content in templates.items():
            template_path = self.templates_dir / filename
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _get_current_user(self, request: Request) -> Optional[User]:
        """Get current user from session/token."""
        # Simple session-based authentication for web interface
        # In production, you might want to use proper session management
        user_id = request.session.get("user_id")
        if user_id:
            return self.auth_manager.get_user(user_id)
        return None
    
    def _require_authentication(self, request: Request) -> User:
        """Require user to be authenticated."""
        user = self._get_current_user(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                detail="Authentication required",
                headers={"Location": "/login"}
            )
        return user
    
    def _setup_routes(self) -> None:
        """Setup web routes."""
        
        @self.app.middleware("http")
        async def add_template_globals(request: Request, call_next):
            """Add global template variables."""
            response = await call_next(request)
            return response
        
        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            """Home page."""
            current_user = self._get_current_user(request)
            if current_user:
                return RedirectResponse("/dashboard")
            else:
                return RedirectResponse("/login")
        
        @self.app.get("/login", response_class=HTMLResponse)
        async def login_form(request: Request):
            """Login form."""
            current_user = self._get_current_user(request)
            if current_user:
                return RedirectResponse("/dashboard")
            
            return self.templates.TemplateResponse("login.html", {
                "request": request,
                "t": t,
                "language": self.i18n.current_language,
                "theme": self.theme_manager.current_theme,
                "theme_css": self.theme_manager.get_css_variables(),
                "available_themes": self.theme_manager.get_available_themes(),
                "available_languages": self.i18n.get_available_languages(),
                "current_user": current_user,
            })
        
        @self.app.post("/login", response_class=HTMLResponse)
        async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
            """Handle login submission."""
            user = self.auth_manager.authenticate_user(username, password)
            if user:
                request.session["user_id"] = user.username
                return RedirectResponse("/dashboard", status_code=302)
            else:
                return self.templates.TemplateResponse("login.html", {
                    "request": request,
                    "t": t,
                    "language": self.i18n.current_language,
                    "theme": self.theme_manager.current_theme,
                    "theme_css": self.theme_manager.get_css_variables(),
                    "available_themes": self.theme_manager.get_available_themes(),
                    "available_languages": self.i18n.get_available_languages(),
                    "current_user": None,
                    "error_message": t("invalid_credentials"),
                })
        
        @self.app.get("/logout")
        async def logout(request: Request):
            """Logout user."""
            request.session.clear()
            return RedirectResponse("/login")
        
        @self.app.get("/dashboard", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Dashboard page."""
            current_user = self._require_authentication(request)
            
            # Get library statistics
            stats = self.library.get_library_stats()
            
            # Get recent activities (mock data for now)
            recent_activities = [
                {"timestamp": "2024-01-15 10:30", "description": "Book 'Python Programming' issued to John Doe"},
                {"timestamp": "2024-01-15 09:15", "description": "New member 'Jane Smith' added"},
                {"timestamp": "2024-01-14 16:45", "description": "Book 'Data Science' returned by Alice Johnson"},
            ]
            
            return self.templates.TemplateResponse("dashboard.html", {
                "request": request,
                "t": t,
                "language": self.i18n.current_language,
                "theme": self.theme_manager.current_theme,
                "theme_css": self.theme_manager.get_css_variables(),
                "available_themes": self.theme_manager.get_available_themes(),
                "available_languages": self.i18n.get_available_languages(),
                "current_user": current_user,
                "stats": stats,
                "recent_activities": recent_activities,
            })
        
        @self.app.post("/api/set-theme")
        async def set_theme(request: Request):
            """Set user theme preference."""
            data = await request.json()
            theme = data.get("theme")
            
            if self.theme_manager.set_current_theme(theme):
                # In a real app, you'd save this to user preferences
                return {"success": True}
            else:
                return {"success": False, "error": "Invalid theme"}
        
        @self.app.post("/api/set-language")
        async def set_language(request: Request):
            """Set user language preference."""
            data = await request.json()
            language = data.get("language")
            
            if self.i18n.set_language(language):
                # In a real app, you'd save this to user preferences
                return {"success": True}
            else:
                return {"success": False, "error": "Invalid language"}
    
    def run(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
        """Run the web interface.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            reload: Enable auto-reload for development
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port, reload=reload)


def create_web_interface(
    library: Optional[Library] = None,
    auth_manager: Optional[AuthManager] = None,
    theme_manager: Optional[ThemeManager] = None,
) -> WebInterface:
    """Create and configure the web interface.
    
    Args:
        library: Library instance
        auth_manager: Authentication manager
        theme_manager: Theme manager
        
    Returns:
        Configured WebInterface instance
    """
    return WebInterface(library, auth_manager, theme_manager)