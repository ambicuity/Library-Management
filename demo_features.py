#!/usr/bin/env python3
"""
Demo script to showcase existing library management features.
This script will demonstrate all current features step by step.
"""

import sys
import os
from library_management_system.library import Library
from library_management_system.models import Book, Member

def demo_existing_features():
    """Demonstrate all existing features of the library management system."""
    print("=== LIBRARY MANAGEMENT SYSTEM DEMO ===\n")
    
    # Initialize library
    library = Library()
    
    print("1. ADDING BOOKS TO LIBRARY")
    print("-" * 30)
    books_to_add = [
        ("The Great Gatsby", "F. Scott Fitzgerald"),
        ("To Kill a Mockingbird", "Harper Lee"),
        ("1984", "George Orwell"),
        ("Pride and Prejudice", "Jane Austen"),
        ("The Catcher in the Rye", "J.D. Salinger")
    ]
    
    for title, author in books_to_add:
        book = Book(title, author)
        library.add_book(book)
        print(f"✓ Added: '{title}' by {author}")
    
    print(f"\nTotal books added: {len(library.books)}")
    
    print("\n2. DISPLAYING ALL BOOKS")
    print("-" * 30)
    library.display_books()
    
    print("\n3. ADDING MEMBERS TO LIBRARY")
    print("-" * 30)
    members_to_add = [
        "Alice Johnson",
        "Bob Smith", 
        "Carol Davis",
        "David Wilson"
    ]
    
    for name in members_to_add:
        member = Member(name)
        library.add_member(member)
        print(f"✓ Added member: {name}")
    
    print(f"\nTotal members added: {len(library.members)}")
    
    print("\n4. DISPLAYING ALL MEMBERS")
    print("-" * 30)
    library.display_members()
    
    print("\n5. ISSUING BOOKS TO MEMBERS")
    print("-" * 30)
    issues = [
        ("The Great Gatsby", "Alice Johnson"),
        ("1984", "Bob Smith"),
        ("Pride and Prejudice", "Carol Davis")
    ]
    
    for title, member_name in issues:
        try:
            library.issue_book(title, member_name)
            print(f"✓ Issued '{title}' to {member_name}")
        except Exception as e:
            print(f"✗ Error issuing '{title}' to {member_name}: {e}")
    
    print("\n6. DISPLAYING UPDATED BOOK LIST (AFTER ISSUING)")
    print("-" * 50)
    library.display_books()
    
    print("\n7. DISPLAYING UPDATED MEMBER LIST (WITH ISSUED BOOKS)")
    print("-" * 55)
    library.display_members()
    
    print("\n8. VIEWING SPECIFIC MEMBER'S BOOKS")
    print("-" * 35)
    for member_name in ["Alice Johnson", "Bob Smith", "David Wilson"]:
        try:
            books = library.get_member_books(member_name)
            print(f"\n{member_name}'s books:")
            if books:
                for book in books:
                    print(f"  - {book}")
            else:
                print("  No books checked out")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n9. RETURNING A BOOK")
    print("-" * 20)
    try:
        library.return_book("The Great Gatsby", "Alice Johnson", "F. Scott Fitzgerald")
        print("✓ Successfully returned 'The Great Gatsby' from Alice Johnson")
    except Exception as e:
        print(f"✗ Error returning book: {e}")
    
    print("\n10. FINAL STATE - BOOKS AFTER RETURN")
    print("-" * 35)
    library.display_books()
    
    print("\n11. FINAL STATE - MEMBERS AFTER RETURN")
    print("-" * 37)
    library.display_members()
    
    print("\n12. SAVING DATA")
    print("-" * 15)
    try:
        library.save_data()
        print("✓ All library data saved successfully")
        
        # Check if files were created
        files_to_check = ["books.txt", "members.txt", "ledger.txt"]
        for file in files_to_check:
            if os.path.exists(file):
                print(f"✓ {file} created")
            else:
                print(f"✗ {file} not found")
                
    except Exception as e:
        print(f"✗ Error saving data: {e}")
    
    print("\n=== DEMO COMPLETE ===")
    print("All existing features have been demonstrated successfully!")
    return library

if __name__ == "__main__":
    demo_existing_features()