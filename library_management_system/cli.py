"""Command-line interface for the Library Management System."""

from typing import Optional

from .library import Library, BookNotFoundError, MemberNotFoundError
from .models import Book, Member


class CLI:
    """Command-line interface for the library management system."""

    def __init__(self, library: Optional[Library] = None) -> None:
        """Initialize the CLI with a library instance.

        Args:
            library: Optional Library instance. If None, creates a default one.
        """
        self.library = library or Library()

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
        print("8. Exit")
        print("=" * 34)

    def get_choice(self) -> int:
        """Get user's menu choice with input validation.

        Returns:
            The user's choice as an integer
        """
        while True:
            try:
                choice = int(input("Enter your choice (1-8): "))
                if 1 <= choice <= 8:
                    return choice
                else:
                    print("Invalid choice. Please enter a number between 1 and 8.")
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

            book = Book(title, author)
            self.library.add_book(book)
            print(f"Book '{title}' by {author} added successfully.")

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
