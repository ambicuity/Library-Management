# Library Management System

This is a simple library management system implemented in Python. It allows you to add books and members, issue books to members, return books from members, and view all the books in the library. The system also tracks the due date for each book that is checked out.

## Features

- Add books to the library
- Add members to the library
- Issue books to members
- Return books from members
- View all the books in the library
- Persist data to files
- Write transactions to a ledger file

## Usage

Run `Library Management.py` to start the system. You will be presented with a menu of options:

1. Add book
2. Add member
3. Issue book
4. Return book
5. Display all books
6. Quit

Enter the number of your choice to perform an operation.

## Data Files

The system uses three data files:

- `books.txt`: Stores information about the books in the library.
- `members.txt`: Stores information about the library members.
- `ledger.txt`: Stores a record of all book issue and return transactions.
