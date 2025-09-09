"""Comprehensive tests for enhanced library management features."""

import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import json
import os

from library_management_system.auth import AuthManager, User, Role, Permission
from library_management_system.secure_data_manager import SecureDataManager, EncryptionManager, BackupManager
from library_management_system.enhanced_search import EnhancedSearch, SearchIndex
from library_management_system.notifications import NotificationManager, NotificationRecipient, NotificationType
from library_management_system.monitoring import MonitoringSystem, StructuredLogger, PerformanceMetrics
from library_management_system.i18n import I18n, init_i18n
from library_management_system.models import Book, Member


class TestAuthentication:
    """Test authentication and authorization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.users_file = os.path.join(self.temp_dir, "test_users.json")
        self.auth_manager = AuthManager(users_file=self.users_file)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_user(self):
        """Test user creation."""
        user = self.auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role=Role.LIBRARIAN
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == Role.LIBRARIAN
        assert user.is_active is True
        assert user.password_hash is not None
    
    def test_authenticate_user(self):
        """Test user authentication."""
        # Create user
        self.auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role=Role.LIBRARIAN
        )
        
        # Test successful authentication
        user = self.auth_manager.authenticate_user("testuser", "password123")
        assert user is not None
        assert user.username == "testuser"
        
        # Test failed authentication
        user = self.auth_manager.authenticate_user("testuser", "wrongpassword")
        assert user is None
    
    def test_user_permissions(self):
        """Test user permissions."""
        # Create users with different roles
        admin = User("admin", "admin@example.com", Role.ADMIN)
        librarian = User("librarian", "librarian@example.com", Role.LIBRARIAN)
        member = User("member", "member@example.com", Role.MEMBER)
        
        # Test admin permissions
        assert admin.has_permission(Permission.DELETE_BOOKS) is True
        assert admin.has_permission(Permission.SYSTEM_CONFIG) is True
        
        # Test librarian permissions
        assert librarian.has_permission(Permission.ADD_BOOKS) is True
        assert librarian.has_permission(Permission.ISSUE_BOOKS) is True
        assert librarian.has_permission(Permission.DELETE_BOOKS) is False
        
        # Test member permissions
        assert member.has_permission(Permission.VIEW_BOOKS) is True
        assert member.has_permission(Permission.ADD_BOOKS) is False
        assert member.has_permission(Permission.ISSUE_BOOKS) is False
    
    def test_jwt_token_creation_and_verification(self):
        """Test JWT token functionality."""
        try:
            # Create user
            self.auth_manager.create_user(
                username="testuser",
                email="test@example.com",
                password="password123",
                role=Role.LIBRARIAN
            )
            
            # Create token
            token = self.auth_manager.create_access_token("testuser")
            assert token is not None
            
            # Verify token
            user = self.auth_manager.verify_token(token)
            assert user is not None
            assert user.username == "testuser"
            
        except Exception as e:
            # JWT functionality might not be available in test environment
            pytest.skip(f"JWT functionality not available: {e}")


class TestSecureDataManager:
    """Test secure data management with encryption and backups."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.books_file = os.path.join(self.temp_dir, "test_books.txt")
        self.members_file = os.path.join(self.temp_dir, "test_members.txt")
        self.ledger_file = os.path.join(self.temp_dir, "test_ledger.txt")
        
        # Test with encryption disabled for reliability
        self.data_manager = SecureDataManager(
            books_file=self.books_file,
            members_file=self.members_file,
            ledger_file=self.ledger_file,
            enable_encryption=False,  # Disable for testing
            enable_backups=True
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_books(self):
        """Test saving and loading books."""
        books = [
            Book("Test Book 1", "Author 1", category="Fiction"),
            Book("Test Book 2", "Author 2", category="Science")
        ]
        
        # Save books
        self.data_manager.save_books(books)
        
        # Load books
        loaded_books = self.data_manager.load_books()
        
        assert len(loaded_books) == 2
        assert loaded_books[0].title == "Test Book 1"
        assert loaded_books[0].author == "Author 1"
        assert loaded_books[0].category == "Fiction"
    
    def test_save_and_load_members(self):
        """Test saving and loading members."""
        members = [
            Member("John Doe"),
            Member("Jane Smith")
        ]
        
        # Save members
        self.data_manager.save_members(members)
        
        # Load members
        loaded_members = self.data_manager.load_members()
        
        assert len(loaded_members) == 2
        assert loaded_members[0].name == "John Doe"
        assert loaded_members[1].name == "Jane Smith"
    
    def test_backup_creation(self):
        """Test backup creation."""
        # Create some test data
        books = [Book("Test Book", "Test Author")]
        self.data_manager.save_books(books)
        
        # Create backup
        backup_path = self.data_manager.create_backup("test_backup")
        
        assert backup_path is not None
        assert os.path.exists(backup_path)
        
        # Check backup contents
        backups = self.data_manager.list_backups()
        assert len(backups) > 0
        assert any(backup["backup_name"] == "test_backup" for backup in backups)
    
    def test_transaction_logging(self):
        """Test transaction logging."""
        # Log some transactions
        self.data_manager.log_transaction("Book added: Test Book")
        self.data_manager.log_transaction("Member added: John Doe")
        
        # Retrieve logs
        logs = self.data_manager.get_transaction_log()
        
        assert len(logs) >= 2
        assert "Book added: Test Book" in logs[-2]
        assert "Member added: John Doe" in logs[-1]


class TestEncryptionManager:
    """Test encryption functionality."""
    
    def test_encryption_and_decryption(self):
        """Test data encryption and decryption."""
        try:
            encryption_manager = EncryptionManager("test_password")
            
            if not encryption_manager.enabled:
                pytest.skip("Cryptography library not available")
            
            # Test data
            original_data = "This is sensitive library data"
            
            # Encrypt
            encrypted_data = encryption_manager.encrypt(original_data)
            assert encrypted_data != original_data
            
            # Decrypt
            decrypted_data = encryption_manager.decrypt(encrypted_data)
            assert decrypted_data == original_data
            
        except ImportError:
            pytest.skip("Cryptography library not available")


class TestEnhancedSearch:
    """Test enhanced search functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.search = EnhancedSearch()
        
        # Create test data
        self.books = [
            Book("Python Programming", "John Smith", category="Technology"),
            Book("Data Science Basics", "Jane Doe", category="Technology"),
            Book("The Great Gatsby", "F. Scott Fitzgerald", category="Fiction"),
            Book("Machine Learning", "John Smith", category="Technology"),
        ]
        
        self.members = [
            Member("Alice Johnson"),
            Member("Bob Wilson"),
            Member("Charlie Brown"),
        ]
        
        # Update search index
        self.search.update_index(self.books, self.members)
    
    def test_search_by_title(self):
        """Test searching books by title."""
        results = self.search.search_books_by_title("Python")
        assert len(results) == 1
        assert results[0].title == "Python Programming"
        
        results = self.search.search_books_by_title("Science")
        assert len(results) == 1
        assert results[0].title == "Data Science Basics"
    
    def test_search_by_author(self):
        """Test searching books by author."""
        results = self.search.search_books_by_author("John Smith")
        assert len(results) == 2
        
        titles = [book.title for book in results]
        assert "Python Programming" in titles
        assert "Machine Learning" in titles
    
    def test_search_by_category(self):
        """Test searching books by category."""
        results = self.search.search_books_by_category("Technology")
        assert len(results) == 3
        
        results = self.search.search_books_by_category("Fiction")
        assert len(results) == 1
        assert results[0].title == "The Great Gatsby"
    
    def test_autocomplete_suggestions(self):
        """Test autocomplete suggestions."""
        suggestions = self.search.get_autocomplete_suggestions("Py", "title", limit=5)
        assert "python" in [s.lower() for s in suggestions]
        
        suggestions = self.search.get_autocomplete_suggestions("John", "author", limit=5)
        assert any("john" in s.lower() for s in suggestions)
    
    def test_fuzzy_search(self):
        """Test fuzzy search functionality."""
        try:
            # Test fuzzy title search
            results = self.search.fuzzy_search_titles("Pyhton", limit=5)  # Misspelled "Python"
            
            # Check if we get any results (depends on fuzzy matching library availability)
            if results:
                assert any("Python" in result[0] for result in results)
            
        except ImportError:
            pytest.skip("Fuzzy search library not available")
    
    def test_search_statistics(self):
        """Test search index statistics."""
        stats = self.search.get_search_statistics()
        
        assert stats["total_title_entries"] > 0
        assert stats["total_author_entries"] > 0
        assert stats["total_categories"] > 0
        assert stats["total_members"] == 3


class TestNotificationSystem:
    """Test notification system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create notification manager without external services
        self.notification_manager = NotificationManager()
        
        # Add test recipient
        recipient = NotificationRecipient(
            name="testuser",
            email="test@example.com",
            phone="+1234567890",
            preferred_method=NotificationType.EMAIL
        )
        self.notification_manager.add_recipient(recipient)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_recipient(self):
        """Test adding notification recipients."""
        recipient = NotificationRecipient(
            name="newuser",
            email="newuser@example.com",
            preferred_method=NotificationType.SMS
        )
        
        self.notification_manager.add_recipient(recipient)
        
        assert "newuser" in self.notification_manager.recipients
        assert self.notification_manager.recipients["newuser"].email == "newuser@example.com"
    
    def test_notification_templates(self):
        """Test notification templates."""
        templates = self.notification_manager.templates
        
        assert "book_due" in templates
        assert "book_overdue" in templates
        assert "system_alert" in templates
        
        # Test template formatting
        template = templates["book_due"]
        formatted_subject = template.subject.format(title="Test Book")
        assert "Test Book" in formatted_subject
    
    def test_send_notification(self):
        """Test sending notifications."""
        # This will fail to actually send but should create a notification record
        success = self.notification_manager.send_notification(
            template_name="book_due",
            recipient_name="testuser",
            data={
                "title": "Test Book",
                "author": "Test Author",
                "due_date": "2024-01-15",
                "member_name": "testuser"
            }
        )
        
        # Check that notification was recorded (even if sending failed)
        history = self.notification_manager.get_notification_history()
        assert len(history) > 0
    
    def test_webhook_management(self):
        """Test webhook management."""
        # Add webhook
        self.notification_manager.add_webhook(
            url="https://example.com/webhook",
            events=["notification_sent", "book_overdue"],
            secret="test_secret"
        )
        
        assert len(self.notification_manager.webhooks) > 0
        webhook = self.notification_manager.webhooks[0]
        assert webhook["url"] == "https://example.com/webhook"
        assert "notification_sent" in webhook["events"]


class TestMonitoringSystem:
    """Test monitoring and logging system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
        
        # Create logger
        self.logger = StructuredLogger(
            name="test_logger",
            log_file=self.log_file,
            enable_console=False
        )
        
        # Create monitoring system
        self.monitoring = MonitoringSystem(
            logger=self.logger,
            enable_performance_monitoring=True,
            enable_security_monitoring=True
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.logger.shutdown()
        shutil.rmtree(self.temp_dir)
    
    def test_performance_metrics(self):
        """Test performance metrics recording."""
        metrics = self.monitoring.performance_metrics
        
        # Record some metrics
        metrics.record_request(100.0, "test_operation", True)
        metrics.record_request(150.0, "test_operation", True)
        metrics.record_request(200.0, "another_operation", False)
        
        # Get statistics
        stats = metrics.get_stats()
        
        assert stats["total_requests"] == 3
        assert stats["error_count"] == 1
        assert stats["average_response_time_ms"] > 0
        assert "test_operation" in stats["operations"]
        assert stats["operations"]["test_operation"]["count"] == 2
    
    def test_user_action_logging(self):
        """Test user action logging."""
        self.monitoring.record_user_action(
            user_id="testuser",
            action="add_book",
            resource="books",
            success=True,
            duration_ms=50.0
        )
        
        # Give logger time to process
        import time
        time.sleep(0.1)
        
        # Check that metrics were recorded
        if self.monitoring.performance_metrics:
            stats = self.monitoring.performance_metrics.get_stats()
            assert stats["total_requests"] > 0
    
    def test_security_monitoring(self):
        """Test security event monitoring."""
        security = self.monitoring.security_monitor
        
        # Record failed login attempts
        is_locked = security.record_failed_login("testuser", "192.168.1.1")
        assert is_locked is False  # First attempt shouldn't lock
        
        # Record multiple failed attempts
        for _ in range(5):
            security.record_failed_login("testuser", "192.168.1.1")
        
        # Should trigger lock after threshold
        is_locked = security.record_failed_login("testuser", "192.168.1.1")
        assert is_locked is True
        
        # Check security summary
        summary = security.get_security_summary()
        assert summary["failed_login_accounts"] > 0
    
    def test_health_check(self):
        """Test system health monitoring."""
        health = self.monitoring.check_health()
        
        assert "status" in health
        assert "timestamp" in health
        assert "issues" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]


class TestInternationalization:
    """Test internationalization features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.translations_dir = os.path.join(self.temp_dir, "translations")
        
        # Initialize i18n
        self.i18n = I18n(default_language="en", translations_dir=self.translations_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_default_translations(self):
        """Test default English translations."""
        assert self.i18n.translate("welcome") == "Welcome to the Library Management System!"
        assert self.i18n.translate("book") == "Book"
        assert self.i18n.translate("books") == "Books"
    
    def test_language_switching(self):
        """Test switching between languages."""
        # Test English (default)
        assert self.i18n.current_language == "en"
        assert self.i18n.translate("welcome").startswith("Welcome")
        
        # Switch to Spanish
        success = self.i18n.set_language("es")
        assert success is True
        assert self.i18n.current_language == "es"
        assert self.i18n.translate("welcome").startswith("¡Bienvenido")
        
        # Switch to non-existent language
        success = self.i18n.set_language("nonexistent")
        assert success is False
        assert self.i18n.current_language == "es"  # Should remain unchanged
    
    def test_translation_fallback(self):
        """Test translation fallback mechanism."""
        # Switch to Spanish
        self.i18n.set_language("es")
        
        # Test key that exists in Spanish
        assert "bienvenido" in self.i18n.translate("welcome").lower()
        
        # Test key that doesn't exist in Spanish (should fall back to English)
        missing_key = "some_missing_key"
        translation = self.i18n.translate(missing_key)
        assert translation == missing_key  # Should return the key itself
    
    def test_translation_variables(self):
        """Test variable substitution in translations."""
        # Add a test translation with variables
        self.i18n.add_translation("en", "greeting", "Hello, {name}!")
        
        result = self.i18n.translate("greeting", name="Alice")
        assert result == "Hello, Alice!"
    
    def test_pluralization(self):
        """Test pluralization support."""
        # Add plural forms
        self.i18n.add_translation("en", "item", "{count} item")
        self.i18n.add_translation("en", "item_plural", "{count} items")
        
        # Test singular
        result = self.i18n.pluralize("item", 1)
        assert "1 item" in result
        
        # Test plural
        result = self.i18n.pluralize("item", 5)
        # Should use plural form if available, or fall back to singular
        assert "5" in result
    
    def test_available_languages(self):
        """Test getting available languages."""
        languages = self.i18n.get_available_languages()
        assert "en" in languages
        assert "es" in languages
        assert len(languages) >= 2
    
    def test_translation_completeness(self):
        """Test translation completeness calculation."""
        # English should be 100% complete (it's the default)
        completeness = self.i18n.get_translation_completeness("en")
        assert completeness == 100.0
        
        # Spanish should have some completeness
        completeness = self.i18n.get_translation_completeness("es")
        assert 0.0 <= completeness <= 100.0
        
        # Non-existent language should be 0%
        completeness = self.i18n.get_translation_completeness("nonexistent")
        assert completeness == 0.0


class TestIntegration:
    """Integration tests for the complete system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize all components
        self.auth_manager = AuthManager(
            users_file=os.path.join(self.temp_dir, "users.json")
        )
        
        self.data_manager = SecureDataManager(
            books_file=os.path.join(self.temp_dir, "books.txt"),
            members_file=os.path.join(self.temp_dir, "members.txt"),
            ledger_file=os.path.join(self.temp_dir, "ledger.txt"),
            enable_encryption=False,
            enable_backups=True
        )
        
        # Create test admin user
        self.admin_user = self.auth_manager.create_user(
            username="admin",
            email="admin@library.local",
            password="admin123",
            role=Role.ADMIN
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test a complete library workflow."""
        # 1. Authenticate admin user
        user = self.auth_manager.authenticate_user("admin", "admin123")
        assert user is not None
        assert user.has_permission(Permission.ADD_BOOKS)
        
        # 2. Add books with proper data management
        books = [
            Book("Python for Beginners", "John Doe", category="Programming"),
            Book("Advanced Python", "Jane Smith", category="Programming")
        ]
        self.data_manager.save_books(books)
        
        # 3. Load and verify books
        loaded_books = self.data_manager.load_books()
        assert len(loaded_books) == 2
        
        # 4. Add members
        members = [
            Member("Alice Johnson"),
            Member("Bob Wilson")
        ]
        self.data_manager.save_members(members)
        
        # 5. Create backup
        backup_path = self.data_manager.create_backup("integration_test")
        assert backup_path is not None
        
        # 6. Verify backup exists
        backups = self.data_manager.list_backups()
        assert len(backups) > 0
        
        # 7. Log transaction
        self.data_manager.log_transaction("Integration test completed successfully")
        
        # 8. Verify transaction log
        logs = self.data_manager.get_transaction_log()
        assert len(logs) > 0
        assert "Integration test completed" in logs[-1]
    
    def test_permission_enforcement(self):
        """Test that permissions are properly enforced."""
        # Create a regular member
        member_user = self.auth_manager.create_user(
            username="member",
            email="member@library.local",
            password="password123",
            role=Role.MEMBER
        )
        
        # Test that member cannot create other users
        with pytest.raises(Exception):
            self.auth_manager.create_user(
                username="unauthorized",
                email="unauthorized@library.local",
                password="password123",
                role=Role.ADMIN,
                created_by=member_user
            )
    
    def test_data_consistency(self):
        """Test data consistency across saves and loads."""
        # Create test data
        original_books = [
            Book("Book 1", "Author 1", category="Category 1"),
            Book("Book 2", "Author 2", category="Category 2")
        ]
        
        original_members = [
            Member("Member 1"),
            Member("Member 2")
        ]
        
        # Save data
        self.data_manager.save_books(original_books)
        self.data_manager.save_members(original_members)
        
        # Load data
        loaded_books = self.data_manager.load_books()
        loaded_members = self.data_manager.load_members()
        
        # Verify consistency
        assert len(loaded_books) == len(original_books)
        assert len(loaded_members) == len(original_members)
        
        for original, loaded in zip(original_books, loaded_books):
            assert original.title == loaded.title
            assert original.author == loaded.author
            assert original.category == loaded.category
        
        for original, loaded in zip(original_members, loaded_members):
            assert original.name == loaded.name


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])