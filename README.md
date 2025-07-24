# Library Management System

A comprehensive library management system implemented in Python that allows you to manage books, members, and track lending transactions with a clean command-line interface.

## Features

- **Book Management**: Add books with title and author information
- **Member Management**: Register library members
- **Book Lending**: Issue books to members with automatic due date calculation
- **Return Processing**: Handle book returns and restore them to available inventory
- **Data Persistence**: Save and load library data using JSON files
- **Transaction Logging**: Track all book issue and return transactions with timestamps
- **Interactive CLI**: User-friendly command-line interface with input validation
- **Comprehensive Testing**: Full test suite with pytest
- **Code Quality**: Formatted with Black, linted with Flake8 and Pylint, type-checked with mypy

## Requirements

- Python 3.8 or higher
- No external dependencies for basic functionality

## Installation

### For Users

1. Clone the repository:
```bash
git clone https://github.com/ambicuity/Library-Management.git
cd Library-Management
```

2. Run the application:
```bash
python library_management.py
```

### For Developers

1. Clone the repository:
```bash
git clone https://github.com/ambicuity/Library-Management.git
cd Library-Management
```

2. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Run tests:
```bash
make test
```

4. Run code quality checks:
```bash
make quality
```

## Usage

Run the application using:
```bash
python library_management.py
```

You will be presented with a menu of options:

1. **Add book** - Add a new book to the library
2. **Add member** - Register a new library member
3. **Issue book** - Lend a book to a member (14-day loan period)
4. **Return book** - Process book returns from members
5. **Display all books** - View all available books in the library
6. **Display all members** - View all registered members and their checked-out books
7. **View member's books** - See what books a specific member has checked out
8. **Exit** - Save data and quit the application

## Project Structure

```
Library-Management/
├── library_management_system/          # Main package
│   ├── __init__.py                    # Package initialization
│   ├── models.py                      # Data models (Book, Member)
│   ├── data_manager.py                # File I/O and data persistence
│   ├── library.py                     # Core library management logic
│   └── cli.py                         # Command-line interface
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── test_models.py                 # Tests for data models
│   ├── test_data_manager.py           # Tests for data persistence
│   └── test_library.py                # Tests for library logic
├── library_management.py              # Main entry point
├── requirements.txt                   # Production dependencies
├── requirements-dev.txt               # Development dependencies
├── pyproject.toml                     # Project configuration
├── .flake8                           # Flake8 configuration
├── .pylintrc                         # Pylint configuration
├── .gitignore                        # Git ignore rules
├── Makefile                          # Development commands
└── README.md                         # This file
```

## Data Files

The system creates and uses three data files in the current directory:

- **`books.txt`**: Stores information about available books in JSON format
- **`members.txt`**: Stores information about registered library members in JSON format
- **`ledger.txt`**: Logs all book issue and return transactions with timestamps

## Development

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run specific test file
python -m pytest tests/test_models.py -v
```

### Code Quality

```bash
# Run all quality checks
make quality

# Individual tools
make format          # Format code with Black
make lint           # Run Flake8 and Pylint
make type-check     # Run mypy type checking
```

### Available Make Commands

- `make help` - Show all available commands
- `make test` - Run the test suite
- `make test-coverage` - Run tests with coverage report
- `make lint` - Run code linting
- `make format` - Format code with Black
- `make type-check` - Run type checking
- `make quality` - Run all quality checks
- `make clean` - Clean up build artifacts
- `make run` - Run the application

## Architecture

The system is built with a modular architecture:

- **Models** (`models.py`): Define `Book` and `Member` classes with validation
- **Data Manager** (`data_manager.py`): Handle file I/O operations and data persistence
- **Library** (`library.py`): Core business logic for library operations
- **CLI** (`cli.py`): User interface and input handling

### Key Features of the Design

- **Type Hints**: Full type annotation for better code documentation and IDE support
- **Error Handling**: Comprehensive exception handling with custom exception types
- **Input Validation**: Robust validation for user inputs and data integrity
- **Separation of Concerns**: Clear separation between data, business logic, and presentation
- **Testability**: Modular design enables comprehensive unit testing
- **Extensibility**: Easy to add new features or modify existing functionality

## Error Handling

The system includes robust error handling for:

- Invalid user inputs (empty names, titles, etc.)
- File I/O errors (permissions, disk space, etc.)
- Data corruption (malformed JSON files)
- Business logic errors (book not found, member not found, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the existing code style
4. Run tests and quality checks (`make quality`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0
- Complete refactoring and modularization of the codebase
- Added comprehensive test suite with 63+ tests
- Implemented proper error handling and input validation
- Added type hints throughout the codebase
- Configured code quality tools (Black, Flake8, Pylint, mypy)
- Improved CLI with better user experience
- Fixed bug in book return functionality that lost author information
- Added proper Python package structure
- Created comprehensive documentation
