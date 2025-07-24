#!/usr/bin/env python3
"""
Library Management System

A simple command-line library management system that allows you to:
- Add books and members
- Issue books to members
- Return books from members
- View available books and member information
- Track transactions in a ledger

Usage:
    python library_management.py
"""

from library_management_system.cli import CLI


def main() -> None:
    """Main entry point for the Library Management System."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
