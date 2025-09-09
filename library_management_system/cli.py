"""Command-line interface for the Library Management System."""

from typing import Optional

from .library import Library, BookNotFoundError, MemberNotFoundError
from .models import Book, Member


class CLI:
    """Command-line interface for the library management system."""

    def __init__(
        self,
        library: Optional[Library] = None,
        auth_manager=None,
        monitoring_system=None,
    ) -> None:
        """Initialize the CLI with a library instance.

        Args:
            library: Optional Library instance. If None, creates a default one.
            auth_manager: Optional authentication manager instance.
            monitoring_system: Optional monitoring system instance.
        """
        self.library = library or Library()
        self.auth_manager = auth_manager
        self.monitoring_system = monitoring_system

    def display_menu(self) -> None:
        """Display the main menu options."""
        print("\n=== Library Management System ===")
        print("1. Add book")
        print("2. Add member")
        print("3. Issue book")
        print("4. Return book")
        print("5. Display all books")
        print("6. Display all members")
        print("7. View member's books")
        print("8. Search books")
        print("9. View overdue books")
        print("10. Browse by category")
        print("11. Exit")
        print("=" * 34)

    def get_choice(self) -> int:
        """Get user's menu choice with input validation.

        Returns:
            The user's choice as an integer
        """
        while True:
            try:
                choice = int(input("Enter your choice (1-11): "))
                if 1 <= choice <= 11:
                    return choice
                else:
                    print("Invalid choice. Please enter a number between 1 and 11.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def add_book(self) -> None:
        """Handle adding a new book to the library."""
        try:
            title = input("Enter book title: ").strip()
            if not title:
                print("Error: Book title cannot be empty.")
                return

            author = input("Enter book author: ").strip()
            if not author:
                print("Error: Book author cannot be empty.")
                return

            category = input(
                "Enter book category (or press Enter for 'General'): "
            ).strip()
            if not category:
                category = "General"

            book = Book(title, author, category=category)
            self.library.add_book(book)
            print(
                f"Book '{title}' by {author} (Category: {category}) added successfully."
            )

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def add_member(self) -> None:
        """Handle adding a new member to the library."""
        try:
            name = input("Enter member name: ").strip()
            if not name:
                print("Error: Member name cannot be empty.")
                return

            member = Member(name)
            self.library.add_member(member)
            print(f"Member '{name}' added successfully.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def issue_book(self) -> None:
        """Handle issuing a book to a member."""
        try:
            title = input("Enter book title to issue: ").strip()
            if not title:
                print("Error: Book title cannot be empty.")
                return

            member_name = input("Enter member name: ").strip()
            if not member_name:
                print("Error: Member name cannot be empty.")
                return

            self.library.issue_book(title, member_name)
            print(f"Book '{title}' issued successfully to {member_name}.")

        except (BookNotFoundError, MemberNotFoundError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def return_book(self) -> None:
        """Handle returning a book from a member."""
        try:
            title = input("Enter book title to return: ").strip()
            if not title:
                print("Error: Book title cannot be empty.")
                return

            member_name = input("Enter member name: ").strip()
            if not member_name:
                print("Error: Member name cannot be empty.")
                return

            author = input("Enter book author: ").strip()
            if not author:
                print("Error: Book author cannot be empty.")
                return

            self.library.return_book(title, member_name, author)
            print(f"Book '{title}' returned successfully from {member_name}.")

        except (BookNotFoundError, MemberNotFoundError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def display_books(self) -> None:
        """Display all available books."""
        self.library.display_books()

    def display_members(self) -> None:
        """Display all library members."""
        self.library.display_members()

    def view_member_books(self) -> None:
        """Display books checked out by a specific member."""
        try:
            member_name = input("Enter member name: ").strip()
            if not member_name:
                print("Error: Member name cannot be empty.")
                return

            books = self.library.get_member_books(member_name)
            if books:
                print(f"\nBooks checked out by {member_name}:")
                for book in books:
                    print(f"- {book}")
            else:
                print(f"{member_name} has no books checked out.")

        except MemberNotFoundError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def search_books(self) -> None:
        """Handle searching for books."""
        try:
            print("\nSearch Options:")
            print("1. Search by title")
            print("2. Search by author")
            print("3. Search both title and author")

            while True:
                try:
                    search_choice = int(input("Choose search type (1-3): "))
                    if 1 <= search_choice <= 3:
                        break
                    else:
                        print("Invalid choice. Please enter 1, 2, or 3.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            query = input("Enter search term: ").strip()
            if not query:
                print("Error: Search term cannot be empty.")
                return

            search_types = {1: "title", 2: "author", 3: "both"}
            search_type = search_types[search_choice]

            self.library.display_search_results(query, search_type)

        except Exception as e:
            print(f"Unexpected error: {e}")

    def view_overdue_books(self) -> None:
        """Display all overdue books."""
        try:
            self.library.display_overdue_books()
        except Exception as e:
            print(f"Unexpected error: {e}")

    def browse_by_category(self) -> None:
        """Handle browsing books by category."""
        try:
            print("\nCategory Options:")
            print("1. View all categories")
            print("2. Browse books in a specific category")

            while True:
                try:
                    choice = int(input("Choose option (1-2): "))
                    if choice in [1, 2]:
                        break
                    else:
                        print("Invalid choice. Please enter 1 or 2.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            if choice == 1:
                self.library.display_categories()
            else:
                category = input("Enter category name: ").strip()
                if not category:
                    print("Error: Category name cannot be empty.")
                    return
                self.library.display_books_by_category(category)

        except Exception as e:
            print(f"Unexpected error: {e}")

    def run(self) -> None:
        """Run the main CLI loop."""
        print("Welcome to the Library Management System!")

        # Load existing data
        try:
            self.library.load_data()
            print("Library data loaded successfully.")
        except ValueError as e:
            print(f"Warning: {e}")
            print("Starting with empty library.")
        except Exception as e:
            print(f"Warning: Failed to load data: {e}")
            print("Starting with empty library.")

        while True:
            try:
                self.display_menu()
                choice = self.get_choice()

                if choice == 1:
                    self.add_book()
                elif choice == 2:
                    self.add_member()
                elif choice == 3:
                    self.issue_book()
                elif choice == 4:
                    self.return_book()
                elif choice == 5:
                    self.display_books()
                elif choice == 6:
                    self.display_members()
                elif choice == 7:
                    self.view_member_books()
                elif choice == 8:
                    self.search_books()
                elif choice == 9:
                    self.view_overdue_books()
                elif choice == 10:
                    self.browse_by_category()
                elif choice == 11:
                    print("Saving library data...")
                    try:
                        self.library.save_data()
                        print("Data saved successfully.")
                    except IOError as e:
                        print(f"Warning: Failed to save data: {e}")
                    print("Thank you for using the Library Management System!")
                    break

            except KeyboardInterrupt:
                print("\n\nProgram interrupted. Saving data...")
                try:
                    self.library.save_data()
                    print("Data saved successfully.")
                except IOError as e:
                    print(f"Warning: Failed to save data: {e}")
                print("Goodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                print("Please try again.")
