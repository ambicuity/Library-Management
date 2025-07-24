"""Tests for the Library class."""

import pytest
from unittest.mock import Mock, patch

from library_management_system.library import (
    Library,
    BookNotFoundError,
    MemberNotFoundError,
)
from library_management_system.models import Book, Member
from library_management_system.data_manager import DataManager


class TestLibrary:
    """Test cases for the Library class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_data_manager = Mock(spec=DataManager)
        self.library = Library(self.mock_data_manager)

    def test_library_initialization(self):
        """Test library initialization."""
        assert self.library.books == []
        assert self.library.members == []
        assert self.library.data_manager == self.mock_data_manager

    def test_library_initialization_default_data_manager(self):
        """Test library initialization with default data manager."""
        library = Library()
        assert isinstance(library.data_manager, DataManager)

    def test_load_data_success(self):
        """Test successful data loading."""
        books = [Book("Book 1", "Author 1")]
        members = [Member("Member 1")]

        self.mock_data_manager.load_books.return_value = books
        self.mock_data_manager.load_members.return_value = members

        self.library.load_data()

        assert self.library.books == books
        assert self.library.members == members
        self.mock_data_manager.load_books.assert_called_once()
        self.mock_data_manager.load_members.assert_called_once()

    def test_load_data_failure(self):
        """Test data loading failure."""
        self.mock_data_manager.load_books.side_effect = ValueError("Load error")

        with pytest.raises(ValueError, match="Failed to load library data"):
            self.library.load_data()

    def test_save_data_success(self):
        """Test successful data saving."""
        self.library.save_data()

        self.mock_data_manager.save_books.assert_called_once_with(self.library.books)
        self.mock_data_manager.save_members.assert_called_once_with(
            self.library.members
        )

    def test_save_data_failure(self):
        """Test data saving failure."""
        self.mock_data_manager.save_books.side_effect = IOError("Save error")

        with pytest.raises(IOError, match="Failed to save library data"):
            self.library.save_data()

    def test_add_book(self):
        """Test adding a book to the library."""
        book = Book("Test Book", "Test Author")
        self.library.add_book(book)

        assert book in self.library.books
        assert len(self.library.books) == 1

    def test_add_book_invalid_type(self):
        """Test adding invalid type as book."""
        with pytest.raises(TypeError, match="Expected Book object"):
            self.library.add_book("not a book")

    def test_add_member(self):
        """Test adding a member to the library."""
        member = Member("Test Member")
        self.library.add_member(member)

        assert member in self.library.members
        assert len(self.library.members) == 1

    def test_add_member_invalid_type(self):
        """Test adding invalid type as member."""
        with pytest.raises(TypeError, match="Expected Member object"):
            self.library.add_member("not a member")

    def test_add_member_duplicate(self):
        """Test adding duplicate member."""
        member1 = Member("John Doe")
        member2 = Member("John Doe")

        self.library.add_member(member1)

        with pytest.raises(ValueError, match="Member 'John Doe' already exists"):
            self.library.add_member(member2)

    def test_find_book(self):
        """Test finding a book by title."""
        book = Book("Test Book", "Test Author")
        self.library.add_book(book)

        found_book = self.library.find_book("Test Book")
        assert found_book == book

        # Test case insensitive search
        found_book = self.library.find_book("test book")
        assert found_book == book

        # Test not found
        not_found = self.library.find_book("Nonexistent Book")
        assert not_found is None

    def test_find_member(self):
        """Test finding a member by name."""
        member = Member("Test Member")
        self.library.add_member(member)

        found_member = self.library.find_member("Test Member")
        assert found_member == member

        # Test case insensitive search
        found_member = self.library.find_member("test member")
        assert found_member == member

        # Test not found
        not_found = self.library.find_member("Nonexistent Member")
        assert not_found is None

    def test_issue_book_success(self):
        """Test successful book issuing."""
        book = Book("Test Book", "Test Author")
        member = Member("Test Member")

        self.library.add_book(book)
        self.library.add_member(member)

        self.library.issue_book("Test Book", "Test Member")

        # Book should be removed from library
        assert book not in self.library.books
        # Book should be added to member's books
        assert "Test Book" in member.books
        # Book should have due date
        assert book.due_date is not None
        # Transaction should be logged
        self.mock_data_manager.log_transaction.assert_called_once_with(
            "Issued", "Test Book", "Test Member"
        )

    def test_issue_book_custom_days(self):
        """Test book issuing with custom loan period."""
        book = Book("Test Book", "Test Author")
        member = Member("Test Member")

        self.library.add_book(book)
        self.library.add_member(member)

        self.library.issue_book("Test Book", "Test Member", days=7)

        assert book not in self.library.books
        assert "Test Book" in member.books
        assert book.due_date is not None

    def test_issue_book_not_found(self):
        """Test issuing non-existent book."""
        member = Member("Test Member")
        self.library.add_member(member)

        with pytest.raises(BookNotFoundError, match="Book 'Nonexistent' not found"):
            self.library.issue_book("Nonexistent", "Test Member")

    def test_issue_book_member_not_found(self):
        """Test issuing book to non-existent member."""
        book = Book("Test Book", "Test Author")
        self.library.add_book(book)

        with pytest.raises(MemberNotFoundError, match="Member 'Nonexistent' not found"):
            self.library.issue_book("Test Book", "Nonexistent")

    def test_issue_book_logging_failure(self):
        """Test book issuing when logging fails."""
        book = Book("Test Book", "Test Author")
        member = Member("Test Member")

        self.library.add_book(book)
        self.library.add_member(member)

        # Make logging fail
        self.mock_data_manager.log_transaction.side_effect = IOError("Log error")

        # Should still succeed even if logging fails
        self.library.issue_book("Test Book", "Test Member")

        assert book not in self.library.books
        assert "Test Book" in member.books

    def test_return_book_success(self):
        """Test successful book return."""
        member = Member("Test Member", ["Test Book"])
        self.library.add_member(member)

        self.library.return_book("Test Book", "Test Member", "Test Author")

        # Book should be removed from member's books
        assert "Test Book" not in member.books
        # Book should be added back to library
        assert len(self.library.books) == 1
        returned_book = self.library.books[0]
        assert returned_book.title == "Test Book"
        assert returned_book.author == "Test Author"
        assert returned_book.due_date is None
        # Transaction should be logged
        self.mock_data_manager.log_transaction.assert_called_once_with(
            "Returned", "Test Book", "Test Member"
        )

    def test_return_book_member_not_found(self):
        """Test returning book from non-existent member."""
        with pytest.raises(MemberNotFoundError, match="Member 'Nonexistent' not found"):
            self.library.return_book("Test Book", "Nonexistent", "Test Author")

    def test_return_book_not_checked_out(self):
        """Test returning book that member doesn't have."""
        member = Member("Test Member")
        self.library.add_member(member)

        with pytest.raises(
            BookNotFoundError, match="Member 'Test Member' does not have book"
        ):
            self.library.return_book("Test Book", "Test Member", "Test Author")

    def test_return_book_logging_failure(self):
        """Test book return when logging fails."""
        member = Member("Test Member", ["Test Book"])
        self.library.add_member(member)

        # Make logging fail
        self.mock_data_manager.log_transaction.side_effect = IOError("Log error")

        # Should still succeed even if logging fails
        self.library.return_book("Test Book", "Test Member", "Test Author")

        assert "Test Book" not in member.books
        assert len(self.library.books) == 1

    def test_get_available_books(self):
        """Test getting available books."""
        book1 = Book("Book 1", "Author 1")
        book2 = Book("Book 2", "Author 2")

        self.library.add_book(book1)
        self.library.add_book(book2)

        books = self.library.get_available_books()
        assert len(books) == 2
        assert book1 in books
        assert book2 in books

        # Should return a copy, not the original list
        books.append("new item")
        assert len(self.library.books) == 2

    def test_get_members(self):
        """Test getting all members."""
        member1 = Member("Member 1")
        member2 = Member("Member 2")

        self.library.add_member(member1)
        self.library.add_member(member2)

        members = self.library.get_members()
        assert len(members) == 2
        assert member1 in members
        assert member2 in members

        # Should return a copy, not the original list
        members.append("new item")
        assert len(self.library.members) == 2

    def test_get_member_books(self):
        """Test getting books checked out by a member."""
        member = Member("Test Member", ["Book 1", "Book 2"])
        self.library.add_member(member)

        books = self.library.get_member_books("Test Member")
        assert books == ["Book 1", "Book 2"]

        # Should return a copy, not the original list
        books.append("Book 3")
        assert len(member.books) == 2

    def test_get_member_books_not_found(self):
        """Test getting books for non-existent member."""
        with pytest.raises(MemberNotFoundError, match="Member 'Nonexistent' not found"):
            self.library.get_member_books("Nonexistent")

    @patch("builtins.print")
    def test_display_books_empty(self, mock_print):
        """Test displaying books when library is empty."""
        self.library.display_books()
        mock_print.assert_called_with("No books available in the library.")

    @patch("builtins.print")
    def test_display_books_with_books(self, mock_print):
        """Test displaying books when library has books."""
        book = Book("Test Book", "Test Author", "2024-01-01")
        self.library.add_book(book)

        self.library.display_books()

        # Check that print was called with expected content
        calls = mock_print.call_args_list
        assert any("Available Books:" in str(call) for call in calls)
        assert any("Test Book" in str(call) for call in calls)
        assert any("Test Author" in str(call) for call in calls)

    @patch("builtins.print")
    def test_display_members_empty(self, mock_print):
        """Test displaying members when library has no members."""
        self.library.display_members()
        mock_print.assert_called_with("No members in the library system.")

    @patch("builtins.print")
    def test_display_members_with_members(self, mock_print):
        """Test displaying members when library has members."""
        member = Member("Test Member", ["Book 1"])
        self.library.add_member(member)

        self.library.display_members()

        # Check that print was called with expected content
        calls = mock_print.call_args_list
        assert any("Library Members:" in str(call) for call in calls)
        assert any("Test Member" in str(call) for call in calls)
        assert any("Book 1" in str(call) for call in calls)
