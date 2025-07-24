"""Main library management system."""

from typing import List, Optional
from datetime import date, timedelta

from .models import Book, Member
from .data_manager import DataManager


class LibraryError(Exception):
    """Base exception for library operations."""

    pass


class BookNotFoundError(LibraryError):
    """Raised when a book is not found."""

    pass


class MemberNotFoundError(LibraryError):
    """Raised when a member is not found."""

    pass


class BookAlreadyIssuedError(LibraryError):
    """Raised when trying to issue a book that's already issued."""

    pass


class Library:
    """Main library management system.

    Handles all library operations including book and member management,
    issuing and returning books, and data persistence.
    """

    def __init__(self, data_manager: Optional[DataManager] = None) -> None:
        """Initialize the library system.

        Args:
            data_manager: Optional data manager instance. If None, creates a default one.
        """
        self.books: List[Book] = []
        self.members: List[Member] = []
        self.data_manager = data_manager or DataManager()

    def load_data(self) -> None:
        """Load all data from files.

        Raises:
            ValueError: If data files are corrupted
        """
        try:
            self.books = self.data_manager.load_books()
            self.members = self.data_manager.load_members()
        except ValueError as e:
            raise ValueError(f"Failed to load library data: {e}")

    def save_data(self) -> None:
        """Save all data to files.

        Raises:
            IOError: If data cannot be saved
        """
        try:
            self.data_manager.save_books(self.books)
            self.data_manager.save_members(self.members)
        except IOError as e:
            raise IOError(f"Failed to save library data: {e}")

    def add_book(self, book: Book) -> None:
        """Add a book to the library.

        Args:
            book: The Book object to add
        """
        if not isinstance(book, Book):
            raise TypeError("Expected Book object")
        self.books.append(book)

    def add_member(self, member: Member) -> None:
        """Add a member to the library.

        Args:
            member: The Member object to add

        Raises:
            ValueError: If member already exists
        """
        if not isinstance(member, Member):
            raise TypeError("Expected Member object")

        if self.find_member(member.name):
            raise ValueError(f"Member '{member.name}' already exists")

        self.members.append(member)

    def find_book(self, title: str) -> Optional[Book]:
        """Find a book by title.

        Args:
            title: The title of the book to find

        Returns:
            The Book object if found, None otherwise
        """
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def find_member(self, name: str) -> Optional[Member]:
        """Find a member by name.

        Args:
            name: The name of the member to find

        Returns:
            The Member object if found, None otherwise
        """
        for member in self.members:
            if member.name.lower() == name.lower():
                return member
        return None

    def issue_book(self, title: str, member_name: str, days: int = 14) -> None:
        """Issue a book to a member.

        Args:
            title: The title of the book to issue
            member_name: The name of the member
            days: Number of days for the loan period (default: 14)

        Raises:
            BookNotFoundError: If the book is not available
            MemberNotFoundError: If the member doesn't exist
        """
        book = self.find_book(title)
        if not book:
            raise BookNotFoundError(f"Book '{title}' not found or not available")

        member = self.find_member(member_name)
        if not member:
            raise MemberNotFoundError(f"Member '{member_name}' not found")

        # Remove book from library and add to member's books
        self.books.remove(book)
        due_date = date.today() + timedelta(days=days)
        book.due_date = due_date.isoformat()
        member.add_book(book.title)

        # Log the transaction
        try:
            self.data_manager.log_transaction("Issued", title, member_name)
        except IOError:
            # Continue operation even if logging fails
            pass

    def return_book(self, title: str, member_name: str, author: str) -> None:
        """Return a book from a member.

        Args:
            title: The title of the book to return
            member_name: The name of the member returning the book
            author: The author of the book (required to preserve book information)

        Raises:
            MemberNotFoundError: If the member doesn't exist
            BookNotFoundError: If the member doesn't have the book
        """
        member = self.find_member(member_name)
        if not member:
            raise MemberNotFoundError(f"Member '{member_name}' not found")

        if not member.has_book(title):
            raise BookNotFoundError(
                f"Member '{member_name}' does not have book '{title}'"
            )

        # Remove book from member and add back to library
        member.remove_book(title)
        returned_book = Book(title, author, None)  # Clear due date
        self.books.append(returned_book)

        # Log the transaction
        try:
            self.data_manager.log_transaction("Returned", title, member_name)
        except IOError:
            # Continue operation even if logging fails
            pass

    def get_available_books(self) -> List[Book]:
        """Get all available books in the library.

        Returns:
            List of available Book objects
        """
        return self.books.copy()

    def get_members(self) -> List[Member]:
        """Get all library members.

        Returns:
            List of Member objects
        """
        return self.members.copy()

    def get_member_books(self, member_name: str) -> List[str]:
        """Get books checked out by a specific member.

        Args:
            member_name: The name of the member

        Returns:
            List of book titles checked out by the member

        Raises:
            MemberNotFoundError: If the member doesn't exist
        """
        member = self.find_member(member_name)
        if not member:
            raise MemberNotFoundError(f"Member '{member_name}' not found")

        return member.books.copy()

    def display_books(self) -> None:
        """Display all available books in the library."""
        if not self.books:
            print("No books available in the library.")
            return

        print("Available Books:")
        print("-" * 50)
        for book in self.books:
            print(f"Title: {book.title}")
            print(f"Author: {book.author}")
            if book.due_date:
                print(f"Due Date: {book.due_date}")
            print("-" * 50)

    def display_members(self) -> None:
        """Display all library members and their checked out books."""
        if not self.members:
            print("No members in the library system.")
            return

        print("Library Members:")
        print("-" * 50)
        for member in self.members:
            print(f"Name: {member.name}")
            if member.books:
                print(f"Books checked out: {', '.join(member.books)}")
            else:
                print("No books checked out")
            print("-" * 50)
