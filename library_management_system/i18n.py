"""Internationalization (i18n) support for the Library Management System."""

import json
from typing import Dict, Optional, Any, List
from pathlib import Path
from datetime import datetime
import locale


class I18n:
    """Internationalization manager."""

    def __init__(
        self, default_language: str = "en", translations_dir: str = "translations"
    ):
        """Initialize i18n manager.

        Args:
            default_language: Default language code
            translations_dir: Directory containing translation files
        """
        self.default_language = default_language
        self.current_language = default_language
        self.translations_dir = Path(translations_dir)
        self.translations: Dict[str, Dict[str, Any]] = {}

        # Create translations directory if it doesn't exist
        self.translations_dir.mkdir(exist_ok=True)

        # Load all available translations
        self._load_translations()

        # Create default translations if none exist
        if not self.translations:
            self._create_default_translations()

    def _load_translations(self) -> None:
        """Load all translation files."""
        for file_path in self.translations_dir.glob("*.json"):
            language_code = file_path.stem
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.translations[language_code] = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load translations for {language_code}: {e}")

    def _create_default_translations(self) -> None:
        """Create default English translations."""
        default_translations = {
            # General
            "welcome": "Welcome to the Library Management System!",
            "goodbye": "Thank you for using the Library Management System!",
            "error": "An error occurred",
            "success": "Operation completed successfully",
            "loading": "Loading...",
            "save": "Save",
            "cancel": "Cancel",
            "delete": "Delete",
            "edit": "Edit",
            "view": "View",
            "search": "Search",
            "filter": "Filter",
            "sort": "Sort",
            "export": "Export",
            "import": "Import",
            "backup": "Backup",
            "restore": "Restore",
            "settings": "Settings",
            "help": "Help",
            "about": "About",
            "logout": "Logout",
            "login": "Login",
            "username": "Username",
            "password": "Password",
            "email": "Email",
            "name": "Name",
            "date": "Date",
            "time": "Time",
            "status": "Status",
            "active": "Active",
            "inactive": "Inactive",
            "available": "Available",
            "unavailable": "Unavailable",
            "yes": "Yes",
            "no": "No",
            "ok": "OK",
            "confirm": "Confirm",
            "required": "Required",
            "optional": "Optional",
            # Menu items
            "menu_add_book": "Add book",
            "menu_add_member": "Add member",
            "menu_issue_book": "Issue book",
            "menu_return_book": "Return book",
            "menu_display_books": "Display all books",
            "menu_display_members": "Display all members",
            "menu_view_member_books": "View member's books",
            "menu_search_books": "Search books",
            "menu_view_overdue": "View overdue books",
            "menu_browse_category": "Browse by category",
            "menu_exit": "Exit",
            # Book management
            "book": "Book",
            "books": "Books",
            "title": "Title",
            "author": "Author",
            "category": "Category",
            "isbn": "ISBN",
            "publication_date": "Publication Date",
            "publisher": "Publisher",
            "pages": "Pages",
            "language": "Language",
            "description": "Description",
            "add_book": "Add Book",
            "edit_book": "Edit Book",
            "delete_book": "Delete Book",
            "book_added": "Book added successfully",
            "book_updated": "Book updated successfully",
            "book_deleted": "Book deleted successfully",
            "book_not_found": "Book not found",
            "book_already_exists": "Book already exists",
            "book_issued": "Book issued successfully",
            "book_returned": "Book returned successfully",
            "book_already_issued": "Book is already issued",
            "book_not_issued": "Book is not currently issued",
            "enter_book_title": "Enter book title",
            "enter_book_author": "Enter book author",
            "enter_book_category": "Enter book category (or press Enter for 'General')",
            "due_date": "Due Date",
            "issue_date": "Issue Date",
            "return_date": "Return Date",
            # Member management
            "member": "Member",
            "members": "Members",
            "member_name": "Member Name",
            "member_id": "Member ID",
            "phone": "Phone",
            "address": "Address",
            "membership_date": "Membership Date",
            "add_member": "Add Member",
            "edit_member": "Edit Member",
            "delete_member": "Delete Member",
            "member_added": "Member added successfully",
            "member_updated": "Member updated successfully",
            "member_deleted": "Member deleted successfully",
            "member_not_found": "Member not found",
            "member_already_exists": "Member already exists",
            "enter_member_name": "Enter member name",
            "books_checked_out": "Books checked out",
            "no_books_checked_out": "No books checked out",
            # Search and filtering
            "search_by_title": "Search by title",
            "search_by_author": "Search by author",
            "search_by_category": "Search by category",
            "search_results": "Search Results",
            "no_results_found": "No results found",
            "found_results": "Found {count} result(s)",
            "filter_by_category": "Filter by category",
            "filter_by_status": "Filter by status",
            "sort_by_title": "Sort by title",
            "sort_by_author": "Sort by author",
            "sort_by_date": "Sort by date",
            "autocomplete_suggestions": "Suggestions",
            "fuzzy_search": "Did you mean",
            # Overdue books
            "overdue_books": "Overdue Books",
            "days_overdue": "Days Overdue",
            "no_overdue_books": "No overdue books found",
            "overdue_notice": "Overdue Notice",
            "book_overdue": "This book is overdue",
            "return_immediately": "Please return immediately",
            # Categories
            "categories": "Categories",
            "all_categories": "All Categories",
            "fiction": "Fiction",
            "non_fiction": "Non-Fiction",
            "science": "Science",
            "history": "History",
            "biography": "Biography",
            "technology": "Technology",
            "art": "Art",
            "music": "Music",
            "sports": "Sports",
            "cooking": "Cooking",
            "travel": "Travel",
            "health": "Health",
            "business": "Business",
            "education": "Education",
            "children": "Children",
            "young_adult": "Young Adult",
            "mystery": "Mystery",
            "romance": "Romance",
            "thriller": "Thriller",
            "horror": "Horror",
            "fantasy": "Fantasy",
            "science_fiction": "Science Fiction",
            "adventure": "Adventure",
            "drama": "Drama",
            "comedy": "Comedy",
            "poetry": "Poetry",
            "philosophy": "Philosophy",
            "religion": "Religion",
            "psychology": "Psychology",
            "sociology": "Sociology",
            "politics": "Politics",
            "economics": "Economics",
            "law": "Law",
            "medicine": "Medicine",
            "engineering": "Engineering",
            "mathematics": "Mathematics",
            "physics": "Physics",
            "chemistry": "Chemistry",
            "biology": "Biology",
            "computer_science": "Computer Science",
            "general": "General",
            # Statistics and reports
            "statistics": "Statistics",
            "reports": "Reports",
            "total_books": "Total Books",
            "total_members": "Total Members",
            "books_issued": "Books Issued",
            "books_available": "Books Available",
            "books_overdue": "Books Overdue",
            "popular_books": "Popular Books",
            "active_members": "Active Members",
            "library_stats": "Library Statistics",
            # User interface
            "dashboard": "Dashboard",
            "navigation": "Navigation",
            "sidebar": "Sidebar",
            "main_content": "Main Content",
            "footer": "Footer",
            "header": "Header",
            "toolbar": "Toolbar",
            "pagination": "Pagination",
            "items_per_page": "Items per page",
            "page": "Page",
            "of": "of",
            "previous": "Previous",
            "next": "Next",
            "first": "First",
            "last": "Last",
            # Forms and validation
            "form_validation_error": "Please correct the following errors:",
            "field_required": "This field is required",
            "invalid_email": "Please enter a valid email address",
            "invalid_phone": "Please enter a valid phone number",
            "invalid_date": "Please enter a valid date",
            "password_too_short": "Password must be at least 6 characters",
            "passwords_do_not_match": "Passwords do not match",
            "invalid_format": "Invalid format",
            "value_too_long": "Value is too long",
            "value_too_short": "Value is too short",
            # Notifications
            "notification": "Notification",
            "notifications": "Notifications",
            "mark_as_read": "Mark as read",
            "mark_all_as_read": "Mark all as read",
            "no_notifications": "No notifications",
            "new_notification": "New notification",
            "due_reminder": "Due Reminder",
            "overdue_notice": "Overdue Notice",
            "book_available": "Book Available",
            "system_alert": "System Alert",
            # Settings
            "language": "Language",
            "theme": "Theme",
            "dark_mode": "Dark Mode",
            "light_mode": "Light Mode",
            "auto_theme": "Auto Theme",
            "notifications_settings": "Notification Settings",
            "email_notifications": "Email Notifications",
            "sms_notifications": "SMS Notifications",
            "push_notifications": "Push Notifications",
            "reminder_settings": "Reminder Settings",
            "days_before_due": "Days before due date",
            # Authentication and authorization
            "login_required": "Login required",
            "access_denied": "Access denied",
            "insufficient_permissions": "Insufficient permissions",
            "session_expired": "Session expired",
            "invalid_credentials": "Invalid username or password",
            "account_locked": "Account temporarily locked",
            "password_reset": "Password Reset",
            "forgot_password": "Forgot Password",
            "change_password": "Change Password",
            "current_password": "Current Password",
            "new_password": "New Password",
            "confirm_password": "Confirm Password",
            "role": "Role",
            "permissions": "Permissions",
            "admin": "Administrator",
            "librarian": "Librarian",
            "user": "User",
            # Error messages
            "error_occurred": "An error occurred",
            "connection_error": "Connection error",
            "server_error": "Server error",
            "not_found": "Not found",
            "forbidden": "Forbidden",
            "unauthorized": "Unauthorized",
            "bad_request": "Bad request",
            "internal_error": "Internal server error",
            "service_unavailable": "Service unavailable",
            "timeout": "Request timeout",
            "network_error": "Network error",
            "database_error": "Database error",
            "file_not_found": "File not found",
            "permission_denied": "Permission denied",
            # Date and time
            "today": "Today",
            "yesterday": "Yesterday",
            "tomorrow": "Tomorrow",
            "this_week": "This week",
            "last_week": "Last week",
            "next_week": "Next week",
            "this_month": "This month",
            "last_month": "Last month",
            "next_month": "Next month",
            "this_year": "This year",
            "last_year": "Last year",
            "next_year": "Next year",
            "january": "January",
            "february": "February",
            "march": "March",
            "april": "April",
            "may": "May",
            "june": "June",
            "july": "July",
            "august": "August",
            "september": "September",
            "october": "October",
            "november": "November",
            "december": "December",
            "monday": "Monday",
            "tuesday": "Tuesday",
            "wednesday": "Wednesday",
            "thursday": "Thursday",
            "friday": "Friday",
            "saturday": "Saturday",
            "sunday": "Sunday",
            # File operations
            "file": "File",
            "files": "Files",
            "upload": "Upload",
            "download": "Download",
            "file_upload": "File Upload",
            "file_download": "File Download",
            "select_file": "Select File",
            "file_selected": "File selected",
            "no_file_selected": "No file selected",
            "file_uploaded": "File uploaded successfully",
            "file_upload_failed": "File upload failed",
            "invalid_file_type": "Invalid file type",
            "file_too_large": "File is too large",
            "export_data": "Export Data",
            "import_data": "Import Data",
            "csv_format": "CSV Format",
            "json_format": "JSON Format",
            "pdf_format": "PDF Format",
            "excel_format": "Excel Format",
            # API and integration
            "api": "API",
            "api_key": "API Key",
            "webhook": "Webhook",
            "webhooks": "Webhooks",
            "integration": "Integration",
            "integrations": "Integrations",
            "external_systems": "External Systems",
            "sync": "Sync",
            "synchronization": "Synchronization",
            "last_sync": "Last sync",
            "sync_now": "Sync now",
            "auto_sync": "Auto sync",
            "manual_sync": "Manual sync",
            # Backup and restore
            "backup_created": "Backup created successfully",
            "backup_failed": "Backup failed",
            "restore_completed": "Restore completed successfully",
            "restore_failed": "Restore failed",
            "backup_schedule": "Backup Schedule",
            "automatic_backup": "Automatic Backup",
            "manual_backup": "Manual Backup",
            "backup_location": "Backup Location",
            "backup_frequency": "Backup Frequency",
            "daily": "Daily",
            "weekly": "Weekly",
            "monthly": "Monthly",
            # Performance and monitoring
            "performance": "Performance",
            "monitoring": "Monitoring",
            "system_health": "System Health",
            "uptime": "Uptime",
            "response_time": "Response Time",
            "error_rate": "Error Rate",
            "requests_per_second": "Requests per Second",
            "memory_usage": "Memory Usage",
            "cpu_usage": "CPU Usage",
            "disk_usage": "Disk Usage",
            "network_usage": "Network Usage",
            "logs": "Logs",
            "log_level": "Log Level",
            "debug": "Debug",
            "info": "Info",
            "warning": "Warning",
            "critical": "Critical",
        }

        # Save default translations
        self.translations[self.default_language] = default_translations
        self._save_translations(self.default_language)

        # Create Spanish translations as an example
        spanish_translations = {
            "welcome": "¡Bienvenido al Sistema de Gestión de Biblioteca!",
            "goodbye": "¡Gracias por usar el Sistema de Gestión de Biblioteca!",
            "error": "Ocurrió un error",
            "success": "Operación completada exitosamente",
            "loading": "Cargando...",
            "save": "Guardar",
            "cancel": "Cancelar",
            "delete": "Eliminar",
            "edit": "Editar",
            "view": "Ver",
            "search": "Buscar",
            "filter": "Filtrar",
            "sort": "Ordenar",
            "export": "Exportar",
            "import": "Importar",
            "backup": "Respaldo",
            "restore": "Restaurar",
            "settings": "Configuración",
            "help": "Ayuda",
            "about": "Acerca de",
            "logout": "Cerrar sesión",
            "login": "Iniciar sesión",
            "username": "Nombre de usuario",
            "password": "Contraseña",
            "email": "Correo electrónico",
            "name": "Nombre",
            "date": "Fecha",
            "time": "Hora",
            "status": "Estado",
            "active": "Activo",
            "inactive": "Inactivo",
            "available": "Disponible",
            "unavailable": "No disponible",
            "yes": "Sí",
            "no": "No",
            "ok": "OK",
            "confirm": "Confirmar",
            "required": "Requerido",
            "optional": "Opcional",
            # Menu items
            "menu_add_book": "Agregar libro",
            "menu_add_member": "Agregar miembro",
            "menu_issue_book": "Prestar libro",
            "menu_return_book": "Devolver libro",
            "menu_display_books": "Mostrar todos los libros",
            "menu_display_members": "Mostrar todos los miembros",
            "menu_view_member_books": "Ver libros del miembro",
            "menu_search_books": "Buscar libros",
            "menu_view_overdue": "Ver libros vencidos",
            "menu_browse_category": "Navegar por categoría",
            "menu_exit": "Salir",
            # Book management
            "book": "Libro",
            "books": "Libros",
            "title": "Título",
            "author": "Autor",
            "category": "Categoría",
            "isbn": "ISBN",
            "publication_date": "Fecha de publicación",
            "publisher": "Editorial",
            "pages": "Páginas",
            "language": "Idioma",
            "description": "Descripción",
            "add_book": "Agregar Libro",
            "edit_book": "Editar Libro",
            "delete_book": "Eliminar Libro",
            "book_added": "Libro agregado exitosamente",
            "book_updated": "Libro actualizado exitosamente",
            "book_deleted": "Libro eliminado exitosamente",
            "book_not_found": "Libro no encontrado",
            "book_already_exists": "El libro ya existe",
            "book_issued": "Libro prestado exitosamente",
            "book_returned": "Libro devuelto exitosamente",
            "book_already_issued": "El libro ya está prestado",
            "book_not_issued": "El libro no está prestado actualmente",
            "enter_book_title": "Ingrese el título del libro",
            "enter_book_author": "Ingrese el autor del libro",
            "enter_book_category": "Ingrese la categoría del libro (o presione Enter para 'General')",
            "due_date": "Fecha de vencimiento",
            "issue_date": "Fecha de préstamo",
            "return_date": "Fecha de devolución",
            # Member management
            "member": "Miembro",
            "members": "Miembros",
            "member_name": "Nombre del miembro",
            "member_id": "ID del miembro",
            "phone": "Teléfono",
            "address": "Dirección",
            "membership_date": "Fecha de membresía",
            "add_member": "Agregar Miembro",
            "edit_member": "Editar Miembro",
            "delete_member": "Eliminar Miembro",
            "member_added": "Miembro agregado exitosamente",
            "member_updated": "Miembro actualizado exitosamente",
            "member_deleted": "Miembro eliminado exitosamente",
            "member_not_found": "Miembro no encontrado",
            "member_already_exists": "El miembro ya existe",
            "enter_member_name": "Ingrese el nombre del miembro",
            "books_checked_out": "Libros prestados",
            "no_books_checked_out": "No hay libros prestados",
            # Language
            "language": "Idioma",
            "english": "Inglés",
            "spanish": "Español",
            "french": "Francés",
            "german": "Alemán",
            "italian": "Italiano",
            "portuguese": "Portugués",
            "chinese": "Chino",
            "japanese": "Japonés",
            "korean": "Coreano",
            "arabic": "Árabe",
            "russian": "Ruso",
            "hindi": "Hindi",
        }

        self.translations["es"] = spanish_translations
        self._save_translations("es")

    def _save_translations(self, language_code: str) -> None:
        """Save translations to file.

        Args:
            language_code: Language code to save
        """
        if language_code in self.translations:
            file_path = self.translations_dir / f"{language_code}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    self.translations[language_code], f, ensure_ascii=False, indent=2
                )

    def set_language(self, language_code: str) -> bool:
        """Set the current language.

        Args:
            language_code: Language code to set

        Returns:
            True if language was set successfully, False otherwise
        """
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False

    def get_available_languages(self) -> List[str]:
        """Get list of available languages.

        Returns:
            List of available language codes
        """
        return list(self.translations.keys())

    def translate(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """Translate a key to the specified language.

        Args:
            key: Translation key
            language: Language code (uses current language if None)
            **kwargs: Variables to substitute in the translation

        Returns:
            Translated string
        """
        language = language or self.current_language

        # Try to get translation from specified language
        if language in self.translations and key in self.translations[language]:
            translation = self.translations[language][key]
        # Fall back to default language
        elif key in self.translations.get(self.default_language, {}):
            translation = self.translations[self.default_language][key]
        # Fall back to the key itself
        else:
            translation = key

        # Substitute variables
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                # If substitution fails, return the original translation
                pass

        return translation

    def t(self, key: str, **kwargs) -> str:
        """Shorthand for translate.

        Args:
            key: Translation key
            **kwargs: Variables to substitute

        Returns:
            Translated string
        """
        return self.translate(key, **kwargs)

    def add_translation(self, language_code: str, key: str, value: str) -> None:
        """Add a new translation.

        Args:
            language_code: Language code
            key: Translation key
            value: Translation value
        """
        if language_code not in self.translations:
            self.translations[language_code] = {}

        self.translations[language_code][key] = value
        self._save_translations(language_code)

    def add_translations(
        self, language_code: str, translations: Dict[str, str]
    ) -> None:
        """Add multiple translations.

        Args:
            language_code: Language code
            translations: Dictionary of translations
        """
        if language_code not in self.translations:
            self.translations[language_code] = {}

        self.translations[language_code].update(translations)
        self._save_translations(language_code)

    def get_language_info(self, language_code: str) -> Dict[str, str]:
        """Get information about a language.

        Args:
            language_code: Language code

        Returns:
            Dictionary with language information
        """
        language_names = {
            "en": {"name": "English", "native_name": "English"},
            "es": {"name": "Spanish", "native_name": "Español"},
            "fr": {"name": "French", "native_name": "Français"},
            "de": {"name": "German", "native_name": "Deutsch"},
            "it": {"name": "Italian", "native_name": "Italiano"},
            "pt": {"name": "Portuguese", "native_name": "Português"},
            "zh": {"name": "Chinese", "native_name": "中文"},
            "ja": {"name": "Japanese", "native_name": "日本語"},
            "ko": {"name": "Korean", "native_name": "한국어"},
            "ar": {"name": "Arabic", "native_name": "العربية"},
            "ru": {"name": "Russian", "native_name": "Русский"},
            "hi": {"name": "Hindi", "native_name": "हिन्दी"},
        }

        return language_names.get(
            language_code, {"name": language_code, "native_name": language_code}
        )

    def format_date(self, date_obj: datetime, format_type: str = "short") -> str:
        """Format a date according to the current language/locale.

        Args:
            date_obj: Date object to format
            format_type: Format type (short, long, medium)

        Returns:
            Formatted date string
        """
        # Try to set locale based on current language
        locale_mappings = {
            "en": "en_US.UTF-8",
            "es": "es_ES.UTF-8",
            "fr": "fr_FR.UTF-8",
            "de": "de_DE.UTF-8",
            "it": "it_IT.UTF-8",
            "pt": "pt_PT.UTF-8",
        }

        try:
            if self.current_language in locale_mappings:
                locale.setlocale(locale.LC_TIME, locale_mappings[self.current_language])
        except locale.Error:
            # If locale is not available, use default
            pass

        # Format based on type
        if format_type == "short":
            return date_obj.strftime("%m/%d/%Y")
        elif format_type == "medium":
            return date_obj.strftime("%b %d, %Y")
        elif format_type == "long":
            return date_obj.strftime("%B %d, %Y")
        elif format_type == "full":
            return date_obj.strftime("%A, %B %d, %Y")
        else:
            return date_obj.strftime("%Y-%m-%d")

    def format_number(self, number: float, format_type: str = "decimal") -> str:
        """Format a number according to the current language/locale.

        Args:
            number: Number to format
            format_type: Format type (decimal, currency, percent)

        Returns:
            Formatted number string
        """
        # Try to set locale based on current language
        locale_mappings = {
            "en": "en_US.UTF-8",
            "es": "es_ES.UTF-8",
            "fr": "fr_FR.UTF-8",
            "de": "de_DE.UTF-8",
            "it": "it_IT.UTF-8",
            "pt": "pt_PT.UTF-8",
        }

        try:
            if self.current_language in locale_mappings:
                locale.setlocale(
                    locale.LC_NUMERIC, locale_mappings[self.current_language]
                )
        except locale.Error:
            # If locale is not available, use default formatting
            if format_type == "currency":
                return f"${number:.2f}"
            elif format_type == "percent":
                return f"{number:.1f}%"
            else:
                return f"{number:,.2f}"

        # Use locale-specific formatting
        if format_type == "currency":
            return locale.currency(number)
        elif format_type == "percent":
            return locale.format_string("%.1f%%", number)
        else:
            return locale.format_string("%.2f", number, grouping=True)

    def pluralize(self, key: str, count: int, **kwargs) -> str:
        """Get the appropriate plural form of a translation.

        Args:
            key: Base translation key
            count: Count to determine plural form
            **kwargs: Additional variables for substitution

        Returns:
            Pluralized translation
        """
        # Simple English pluralization rules
        if count == 1:
            return self.translate(key, count=count, **kwargs)
        else:
            # Try to find plural form
            plural_key = f"{key}_plural"
            if (
                self.current_language in self.translations
                and plural_key in self.translations[self.current_language]
            ):
                return self.translate(plural_key, count=count, **kwargs)
            else:
                # Use singular form with count
                return self.translate(key, count=count, **kwargs)

    def get_translation_completeness(self, language_code: str) -> float:
        """Get the translation completeness percentage for a language.

        Args:
            language_code: Language code to check

        Returns:
            Percentage of translations completed (0.0 to 100.0)
        """
        if language_code not in self.translations:
            return 0.0

        default_keys = set(self.translations.get(self.default_language, {}).keys())
        language_keys = set(self.translations[language_code].keys())

        if not default_keys:
            return 100.0

        completeness = len(language_keys.intersection(default_keys)) / len(default_keys)
        return completeness * 100.0

    def export_translations(self, language_code: str, file_path: str) -> bool:
        """Export translations to a file.

        Args:
            language_code: Language code to export
            file_path: Output file path

        Returns:
            True if export was successful, False otherwise
        """
        if language_code not in self.translations:
            return False

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    self.translations[language_code], f, ensure_ascii=False, indent=2
                )
            return True
        except (IOError, OSError):
            return False

    def import_translations(self, language_code: str, file_path: str) -> bool:
        """Import translations from a file.

        Args:
            language_code: Language code to import
            file_path: Input file path

        Returns:
            True if import was successful, False otherwise
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                translations = json.load(f)

            if not isinstance(translations, dict):
                return False

            self.translations[language_code] = translations
            self._save_translations(language_code)
            return True
        except (IOError, OSError, json.JSONDecodeError):
            return False


# Global i18n instance
_i18n = None


def get_i18n() -> I18n:
    """Get the global i18n instance.

    Returns:
        Global I18n instance
    """
    global _i18n
    if _i18n is None:
        _i18n = I18n()
    return _i18n


def init_i18n(
    default_language: str = "en", translations_dir: str = "translations"
) -> I18n:
    """Initialize the global i18n instance.

    Args:
        default_language: Default language code
        translations_dir: Directory containing translation files

    Returns:
        Initialized I18n instance
    """
    global _i18n
    _i18n = I18n(default_language, translations_dir)
    return _i18n


def t(key: str, **kwargs) -> str:
    """Global translation function.

    Args:
        key: Translation key
        **kwargs: Variables to substitute

    Returns:
        Translated string
    """
    return get_i18n().translate(key, **kwargs)


def set_language(language_code: str) -> bool:
    """Set the global language.

    Args:
        language_code: Language code to set

    Returns:
        True if language was set successfully, False otherwise
    """
    return get_i18n().set_language(language_code)
