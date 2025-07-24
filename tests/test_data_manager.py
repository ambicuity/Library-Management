"""Tests for the DataManager class."""

import json
import os
import tempfile
import pytest

from library_management_system.data_manager import DataManager
from library_management_system.models import Book, Member


class TestDataManager:
    """Test cases for the DataManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary files for testing
        self.temp_dir = tempfile.mkdtemp()
        self.books_file = os.path.join(self.temp_dir, "test_books.txt")
        self.members_file = os.path.join(self.temp_dir, "test_members.txt")
        self.ledger_file = os.path.join(self.temp_dir, "test_ledger.txt")

        self.data_manager = DataManager(
            books_file=self.books_file,
            members_file=self.members_file,
            ledger_file=self.ledger_file,
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary files
        for file_path in [self.books_file, self.members_file, self.ledger_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.rmdir(self.temp_dir)

    def test_load_books_empty_file(self):
        """Test loading books when file doesn't exist."""
        books = self.data_manager.load_books()
        assert books == []

    def test_save_and_load_books(self):
        """Test saving and loading books."""
        books = [Book("Book 1", "Author 1"), Book("Book 2", "Author 2", "2024-01-01")]

        # Save books
        self.data_manager.save_books(books)
        assert os.path.exists(self.books_file)

        # Load books
        loaded_books = self.data_manager.load_books()
        assert len(loaded_books) == 2
        assert loaded_books[0].title == "Book 1"
        assert loaded_books[0].author == "Author 1"
        assert loaded_books[0].due_date is None
        assert loaded_books[1].title == "Book 2"
        assert loaded_books[1].author == "Author 2"
        assert loaded_books[1].due_date == "2024-01-01"

    def test_load_books_corrupted_data(self):
        """Test loading books with corrupted data."""
        # Write invalid JSON
        with open(self.books_file, "w") as f:
            f.write("invalid json")

        with pytest.raises(ValueError, match="Error loading books data"):
            self.data_manager.load_books()

    def test_load_books_missing_fields(self):
        """Test loading books with missing required fields."""
        # Write JSON with missing fields
        invalid_data = [
            {"title": "Book 1"},  # Missing author
            {"author": "Author 2"},  # Missing title
            {"title": "Book 3", "author": "Author 3"},  # Valid
        ]

        with open(self.books_file, "w") as f:
            json.dump(invalid_data, f)

        books = self.data_manager.load_books()
        # Should only load the valid book
        assert len(books) == 1
        assert books[0].title == "Book 3"

    def test_load_members_empty_file(self):
        """Test loading members when file doesn't exist."""
        members = self.data_manager.load_members()
        assert members == []

    def test_save_and_load_members(self):
        """Test saving and loading members."""
        members = [Member("Member 1"), Member("Member 2", ["Book 1", "Book 2"])]

        # Save members
        self.data_manager.save_members(members)
        assert os.path.exists(self.members_file)

        # Load members
        loaded_members = self.data_manager.load_members()
        assert len(loaded_members) == 2
        assert loaded_members[0].name == "Member 1"
        assert loaded_members[0].books == []
        assert loaded_members[1].name == "Member 2"
        assert loaded_members[1].books == ["Book 1", "Book 2"]

    def test_load_members_corrupted_data(self):
        """Test loading members with corrupted data."""
        # Write invalid JSON
        with open(self.members_file, "w") as f:
            f.write("invalid json")

        with pytest.raises(ValueError, match="Error loading members data"):
            self.data_manager.load_members()

    def test_load_members_missing_fields(self):
        """Test loading members with missing required fields."""
        # Write JSON with missing fields
        invalid_data = [
            {"books": ["Book 1"]},  # Missing name
            {"name": "Member 2", "books": ["Book 2"]},  # Valid
        ]

        with open(self.members_file, "w") as f:
            json.dump(invalid_data, f)

        members = self.data_manager.load_members()
        # Should only load the valid member
        assert len(members) == 1
        assert members[0].name == "Member 2"

    def test_log_transaction(self):
        """Test logging a transaction."""
        self.data_manager.log_transaction("Issued", "Test Book", "Test Member")

        assert os.path.exists(self.ledger_file)
        with open(self.ledger_file, "r") as f:
            content = f.read()
            assert "Issued" in content
            assert "Test Book" in content
            assert "Test Member" in content
            assert "to" in content  # For issued action

    def test_log_multiple_transactions(self):
        """Test logging multiple transactions."""
        self.data_manager.log_transaction("Issued", "Book 1", "Member 1")
        self.data_manager.log_transaction("Returned", "Book 2", "Member 2")

        history = self.data_manager.get_transaction_history()
        assert len(history) == 2
        assert "Issued" in history[0]
        assert "to" in history[0]
        assert "Returned" in history[1]
        assert "from" in history[1]

    def test_get_transaction_history_empty(self):
        """Test getting transaction history when no transactions exist."""
        history = self.data_manager.get_transaction_history()
        assert history == []

    def test_save_books_io_error(self):
        """Test handling IO error when saving books."""
        # Use an invalid file path
        invalid_data_manager = DataManager(books_file="/invalid/path/books.txt")
        books = [Book("Test", "Author")]

        with pytest.raises(IOError, match="Error saving books data"):
            invalid_data_manager.save_books(books)

    def test_save_members_io_error(self):
        """Test handling IO error when saving members."""
        # Use an invalid file path
        invalid_data_manager = DataManager(members_file="/invalid/path/members.txt")
        members = [Member("Test")]

        with pytest.raises(IOError, match="Error saving members data"):
            invalid_data_manager.save_members(members)

    def test_log_transaction_io_error(self):
        """Test handling IO error when logging transaction."""
        # Use an invalid file path
        invalid_data_manager = DataManager(ledger_file="/invalid/path/ledger.txt")

        with pytest.raises(IOError, match="Error writing to ledger"):
            invalid_data_manager.log_transaction("Issued", "Book", "Member")
