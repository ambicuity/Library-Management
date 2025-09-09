#!/usr/bin/env python3
"""
Enhanced demo script to showcase new library management features.
This script will demonstrate all features including the new ones.
"""

import sys
import os
from datetime import date, timedelta
from library_management_system.library import Library
from library_management_system.models import Book, Member

def demo_enhanced_features():
    """Demonstrate all features including new enhancements."""
    print("=== ENHANCED LIBRARY MANAGEMENT SYSTEM DEMO ===\n")
    
    # Initialize library
    library = Library()
    
    print("1. ADDING SAMPLE BOOKS TO LIBRARY")
    print("-" * 40)
    books_to_add = [
        ("The Great Gatsby", "F. Scott Fitzgerald"),
        ("To Kill a Mockingbird", "Harper Lee"),
        ("1984", "George Orwell"),
        ("Pride and Prejudice", "Jane Austen"),
        ("The Catcher in the Rye", "J.D. Salinger"),
        ("The Lord of the Rings", "J.R.R. Tolkien"),
        ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling"),
        ("The Hobbit", "J.R.R. Tolkien"),
        ("Jane Eyre", "Charlotte Bronte"),
        ("Wuthering Heights", "Emily Bronte")
    ]
    
    for title, author in books_to_add:
        book = Book(title, author)
        library.add_book(book)
        print(f"✓ Added: '{title}' by {author}")
    
    print(f"\nTotal books added: {len(library.books)}")
    
    print("\n2. ADDING SAMPLE MEMBERS")
    print("-" * 25)
    members_to_add = [
        "Alice Johnson",
        "Bob Smith", 
        "Carol Davis",
        "David Wilson",
        "Emma Brown"
    ]
    
    for name in members_to_add:
        member = Member(name)
        library.add_member(member)
        print(f"✓ Added member: {name}")
    
    print("\n3. TESTING SEARCH FUNCTIONALITY")
    print("-" * 35)
    
    # Test search by title
    print("\n3a. Search by Title: 'Harry'")
    library.display_search_results("Harry", "title")
    
    # Test search by author
    print("\n3b. Search by Author: 'Tolkien'")
    library.display_search_results("Tolkien", "author")
    
    # Test search both
    print("\n3c. Search Both Title and Author: 'Pride'")
    library.display_search_results("Pride", "both")
    
    # Test search with no results
    print("\n3d. Search with No Results: 'Nonexistent'")
    library.display_search_results("Nonexistent", "title")
    
    print("\n4. ISSUING BOOKS TO MEMBERS")
    print("-" * 30)
    issues = [
        ("The Great Gatsby", "Alice Johnson"),
        ("1984", "Bob Smith"),
        ("Pride and Prejudice", "Carol Davis"),
        ("The Lord of the Rings", "David Wilson"),
        ("Harry Potter and the Sorcerer's Stone", "Emma Brown")
    ]
    
    for title, member_name in issues:
        try:
            library.issue_book(title, member_name)
            print(f"✓ Issued '{title}' to {member_name}")
        except Exception as e:
            print(f"✗ Error issuing '{title}' to {member_name}: {e}")
    
    print("\n5. TESTING OVERDUE BOOKS FUNCTIONALITY")
    print("-" * 45)
    
    # Create an artificial overdue situation by issuing a book with a past due date
    # First, manually manipulate one member's checked out book to be overdue
    member = library.find_member("Alice Johnson")
    if member and member.checked_out_books:
        # Make it 5 days overdue
        overdue_date = date.today() - timedelta(days=5)
        for book_title in member.checked_out_books:
            member.checked_out_books[book_title].due_date = overdue_date.isoformat()
            break
    
    print("Creating artificial overdue scenario for demonstration...")
    library.display_overdue_books()
    
    print("\n6. SEARCHING AVAILABLE BOOKS (AFTER ISSUING)")
    print("-" * 50)
    print("\n6a. Search for remaining Tolkien books:")
    library.display_search_results("Tolkien", "author")
    
    print("\n6b. Search for books with 'the' in title:")
    library.display_search_results("the", "title")
    
    print("\n7. DISPLAYING CURRENT LIBRARY STATE")
    print("-" * 40)
    print("\n7a. Available Books:")
    library.display_books()
    
    print("\n7b. All Members:")
    library.display_members()
    
    print("\n8. RETURNING A BOOK")
    print("-" * 20)
    try:
        library.return_book("The Great Gatsby", "Alice Johnson", "F. Scott Fitzgerald")
        print("✓ Successfully returned 'The Great Gatsby' from Alice Johnson")
    except Exception as e:
        print(f"✗ Error returning book: {e}")
    
    print("\n9. FINAL OVERDUE CHECK (AFTER RETURN)")
    print("-" * 40)
    library.display_overdue_books()
    
    print("\n10. FINAL SEARCH TEST")
    print("-" * 20)
    print("Search for 'Great Gatsby' (should be available again):")
    library.display_search_results("Great Gatsby", "title")
    
    print("\n11. LIBRARY STATISTICS")
    print("-" * 25)
    total_books = len(library.books)
    total_members = len(library.members)
    total_issued = sum(len(member.books) for member in library.members)
    overdue_count = len(library.get_overdue_books())
    
    print(f"📚 Total books in library: {total_books}")
    print(f"👥 Total registered members: {total_members}")
    print(f"📖 Total books currently issued: {total_issued}")
    print(f"⚠️  Total overdue books: {overdue_count}")
    
    print("\n12. SAVING DATA")
    print("-" * 15)
    try:
        library.save_data()
        print("✓ All library data saved successfully")
        
        # Check if files were created
        files_to_check = ["books.txt", "members.txt", "ledger.txt"]
        for file in files_to_check:
            if os.path.exists(file):
                file_size = os.path.getsize(file)
                print(f"✓ {file} created ({file_size} bytes)")
            else:
                print(f"✗ {file} not found")
                
    except Exception as e:
        print(f"✗ Error saving data: {e}")
    
    print("\n=== ENHANCED DEMO COMPLETE ===")
    print("All existing and new features have been demonstrated successfully!")
    
    return library

if __name__ == "__main__":
    demo_enhanced_features()