"""Data persistence manager for the Library Management System."""

import json
import os
from typing import List
from datetime import datetime

from .models import Book, Member


class DataManager:
    """Handles data persistence for books, members, and transaction logging."""

    def __init__(
        self,
        books_file: str = "books.txt",
        members_file: str = "members.txt",
        ledger_file: str = "ledger.txt",
    ) -> None:
        """Initialize the data manager with file paths.

        Args:
            books_file: Path to the books data file
            members_file: Path to the members data file
            ledger_file: Path to the transaction ledger file
        """
        self.books_file = books_file
        self.members_file = members_file
        self.ledger_file = ledger_file

    def load_books(self) -> List[Book]:
        """Load books from the data file.

        Returns:
            List of Book objects

        Raises:
            ValueError: If the data file is corrupted
        """
        if not os.path.exists(self.books_file):
            return []

        try:
            with open(self.books_file, "r", encoding="utf-8") as f:
                books_data = json.load(f)
                books = []
                for book_dict in books_data:
                    if not isinstance(book_dict, dict):
                        continue
                    if "title" not in book_dict or "author" not in book_dict:
                        continue
                    books.append(
                        Book(
                            title=book_dict["title"],
                            author=book_dict["author"],
                            due_date=book_dict.get("due_date"),
                        )
                    )
                return books
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Error loading books data: {e}")

    def save_books(self, books: List[Book]) -> None:
        """Save books to the data file.

        Args:
            books: List of Book objects to save

        Raises:
            IOError: If the file cannot be written
        """
        try:
            books_data = [book.__dict__ for book in books]
            with open(self.books_file, "w", encoding="utf-8") as f:
                json.dump(books_data, f, indent=2)
        except IOError as e:
            raise IOError(f"Error saving books data: {e}")

    def load_members(self) -> List[Member]:
        """Load members from the data file.

        Returns:
            List of Member objects

        Raises:
            ValueError: If the data file is corrupted
        """
        if not os.path.exists(self.members_file):
            return []

        try:
            with open(self.members_file, "r", encoding="utf-8") as f:
                members_data = json.load(f)
                members = []
                for member_dict in members_data:
                    if not isinstance(member_dict, dict):
                        continue
                    if "name" not in member_dict:
                        continue
                    members.append(
                        Member(
                            name=member_dict["name"], books=member_dict.get("books", [])
                        )
                    )
                return members
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Error loading members data: {e}")

    def save_members(self, members: List[Member]) -> None:
        """Save members to the data file.

        Args:
            members: List of Member objects to save

        Raises:
            IOError: If the file cannot be written
        """
        try:
            members_data = [member.__dict__ for member in members]
            with open(self.members_file, "w", encoding="utf-8") as f:
                json.dump(members_data, f, indent=2)
        except IOError as e:
            raise IOError(f"Error saving members data: {e}")

    def log_transaction(self, action: str, book_title: str, member_name: str) -> None:
        """Log a transaction to the ledger file.

        Args:
            action: The action performed (e.g., "Issued", "Returned")
            book_title: The title of the book involved
            member_name: The name of the member involved

        Raises:
            IOError: If the ledger file cannot be written
        """
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"{timestamp} - {action} \"{book_title}\" {'to' if action == 'Issued' else 'from'} {member_name}\n"

            with open(self.ledger_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except IOError as e:
            raise IOError(f"Error writing to ledger: {e}")

    def get_transaction_history(self) -> List[str]:
        """Get the transaction history from the ledger file.

        Returns:
            List of transaction log entries

        Raises:
            IOError: If the ledger file cannot be read
        """
        if not os.path.exists(self.ledger_file):
            return []

        try:
            with open(self.ledger_file, "r", encoding="utf-8") as f:
                return f.readlines()
        except IOError as e:
            raise IOError(f"Error reading ledger: {e}")
