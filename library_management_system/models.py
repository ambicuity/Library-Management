"""Data models for the Library Management System."""

from typing import List, Optional, Dict


class CheckedOutBook:
    """Represents a book that is checked out to a member.
    
    Attributes:
        title (str): The title of the book
        author (str): The author of the book
        due_date (str): The due date when the book should be returned
    """
    
    def __init__(self, title: str, author: str, due_date: str) -> None:
        """Initialize a new CheckedOutBook instance.
        
        Args:
            title: The title of the book
            author: The author of the book
            due_date: The due date for the book
        """
        if not title or not title.strip():
            raise ValueError("Book title cannot be empty")
        if not author or not author.strip():
            raise ValueError("Book author cannot be empty")
        if not due_date or not due_date.strip():
            raise ValueError("Due date cannot be empty")
            
        self.title = title.strip()
        self.author = author.strip()
        self.due_date = due_date.strip()
    
    def __repr__(self) -> str:
        """Return a string representation of the checked out book."""
        return f"CheckedOutBook(title='{self.title}', author='{self.author}', due_date='{self.due_date}')"


class Book:
    """Represents a book in the library system.

    Attributes:
        title (str): The title of the book
        author (str): The author of the book
        due_date (Optional[str]): The due date when the book should be returned
        category (str): The category/genre of the book
    """

    def __init__(self, title: str, author: str, due_date: Optional[str] = None, category: str = "General") -> None:
        """Initialize a new Book instance.

        Args:
            title: The title of the book
            author: The author of the book
            due_date: The due date for the book (if checked out)
            category: The category/genre of the book
        """
        if not title or not title.strip():
            raise ValueError("Book title cannot be empty")
        if not author or not author.strip():
            raise ValueError("Book author cannot be empty")

        self.title = title.strip()
        self.author = author.strip()
        self.due_date = due_date
        self.category = category.strip() if category else "General"

    def __repr__(self) -> str:
        """Return a string representation of the book."""
        return f"Book(title='{self.title}', author='{self.author}', due_date='{self.due_date}', category='{self.category}')"

    def __eq__(self, other: object) -> bool:
        """Check if two books are equal based on title and author."""
        if not isinstance(other, Book):
            return False
        return self.title == other.title and self.author == other.author


class Member:
    """Represents a library member.

    Attributes:
        name (str): The name of the member
        books (List[str]): List of book titles currently checked out by the member
        checked_out_books (Dict[str, CheckedOutBook]): Dictionary mapping book titles to CheckedOutBook objects
    """

    def __init__(self, name: str, books: Optional[List[str]] = None) -> None:
        """Initialize a new Member instance.

        Args:
            name: The name of the member
            books: List of book titles currently checked out
        """
        if not name or not name.strip():
            raise ValueError("Member name cannot be empty")

        self.name = name.strip()
        self.books = books if books else []
        self.checked_out_books: Dict[str, CheckedOutBook] = {}

    def __repr__(self) -> str:
        """Return a string representation of the member."""
        return f"Member(name='{self.name}', books={self.books})"

    def __eq__(self, other: object) -> bool:
        """Check if two members are equal based on name."""
        if not isinstance(other, Member):
            return False
        return self.name == other.name

    def has_book(self, title: str) -> bool:
        """Check if the member has a specific book checked out.

        Args:
            title: The title of the book to check

        Returns:
            True if the member has the book, False otherwise
        """
        return title in self.books

    def add_book(self, title: str, author: str = "", due_date: str = "") -> None:
        """Add a book to the member's checked out books.

        Args:
            title: The title of the book to add
            author: The author of the book (for tracking due dates)
            due_date: The due date of the book
        """
        if title not in self.books:
            self.books.append(title)
            
        if author and due_date:
            self.checked_out_books[title] = CheckedOutBook(title, author, due_date)

    def remove_book(self, title: str) -> bool:
        """Remove a book from the member's checked out books.

        Args:
            title: The title of the book to remove

        Returns:
            True if the book was removed, False if it wasn't found
        """
        if title in self.books:
            self.books.remove(title)
            # Also remove from checked out books tracking
            if title in self.checked_out_books:
                del self.checked_out_books[title]
            return True
        return False

    def get_checked_out_book(self, title: str) -> Optional[CheckedOutBook]:
        """Get the CheckedOutBook object for a specific title.
        
        Args:
            title: The title of the book
            
        Returns:
            CheckedOutBook object if found, None otherwise
        """
        return self.checked_out_books.get(title)
