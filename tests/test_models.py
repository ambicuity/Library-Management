"""Tests for the Book and Member models."""

import pytest
from library_management_system.models import Book, Member


class TestBook:
    """Test cases for the Book class."""

    def test_book_creation(self):
        """Test creating a book with valid data."""
        book = Book("The Python Guide", "John Doe")
        assert book.title == "The Python Guide"
        assert book.author == "John Doe"
        assert book.due_date is None

    def test_book_creation_with_due_date(self):
        """Test creating a book with a due date."""
        book = Book("Test Book", "Test Author", "2024-01-01")
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.due_date == "2024-01-01"

    def test_book_creation_empty_title(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Book title cannot be empty"):
            Book("", "Author")

    def test_book_creation_empty_author(self):
        """Test that empty author raises ValueError."""
        with pytest.raises(ValueError, match="Book author cannot be empty"):
            Book("Title", "")

    def test_book_creation_whitespace_title(self):
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="Book title cannot be empty"):
            Book("   ", "Author")

    def test_book_creation_whitespace_author(self):
        """Test that whitespace-only author raises ValueError."""
        with pytest.raises(ValueError, match="Book author cannot be empty"):
            Book("Title", "   ")

    def test_book_strips_whitespace(self):
        """Test that title and author are stripped of whitespace."""
        book = Book("  Title  ", "  Author  ")
        assert book.title == "Title"
        assert book.author == "Author"

    def test_book_equality(self):
        """Test book equality comparison."""
        book1 = Book("Title", "Author")
        book2 = Book("Title", "Author")
        book3 = Book("Different", "Author")

        assert book1 == book2
        assert book1 != book3
        assert book1 != "not a book"

    def test_book_repr(self):
        """Test book string representation."""
        book = Book("Title", "Author", "2024-01-01")
        expected = "Book(title='Title', author='Author', due_date='2024-01-01')"
        assert repr(book) == expected


class TestMember:
    """Test cases for the Member class."""

    def test_member_creation(self):
        """Test creating a member with valid data."""
        member = Member("Jane Smith")
        assert member.name == "Jane Smith"
        assert member.books == []

    def test_member_creation_with_books(self):
        """Test creating a member with existing books."""
        books = ["Book 1", "Book 2"]
        member = Member("John Doe", books)
        assert member.name == "John Doe"
        assert member.books == books

    def test_member_creation_empty_name(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Member name cannot be empty"):
            Member("")

    def test_member_creation_whitespace_name(self):
        """Test that whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="Member name cannot be empty"):
            Member("   ")

    def test_member_strips_whitespace(self):
        """Test that name is stripped of whitespace."""
        member = Member("  John Doe  ")
        assert member.name == "John Doe"

    def test_member_equality(self):
        """Test member equality comparison."""
        member1 = Member("John Doe")
        member2 = Member("John Doe")
        member3 = Member("Jane Smith")

        assert member1 == member2
        assert member1 != member3
        assert member1 != "not a member"

    def test_member_repr(self):
        """Test member string representation."""
        member = Member("John Doe", ["Book 1"])
        expected = "Member(name='John Doe', books=['Book 1'])"
        assert repr(member) == expected

    def test_has_book(self):
        """Test checking if member has a book."""
        member = Member("John", ["Book 1", "Book 2"])
        assert member.has_book("Book 1") is True
        assert member.has_book("Book 3") is False

    def test_add_book(self):
        """Test adding a book to member."""
        member = Member("John")
        member.add_book("New Book")
        assert "New Book" in member.books

        # Adding same book again should not duplicate
        member.add_book("New Book")
        assert member.books.count("New Book") == 1

    def test_remove_book(self):
        """Test removing a book from member."""
        member = Member("John", ["Book 1", "Book 2"])

        # Remove existing book
        result = member.remove_book("Book 1")
        assert result is True
        assert "Book 1" not in member.books
        assert "Book 2" in member.books

        # Try to remove non-existing book
        result = member.remove_book("Book 3")
        assert result is False
