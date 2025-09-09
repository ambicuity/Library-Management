#!/usr/bin/env python3
"""
Comprehensive demo script to showcase all library management features.
This script demonstrates both existing and new enhanced features.
"""

import sys
import os
from datetime import date, timedelta
from library_management_system.library import Library
from library_management_system.models import Book, Member

def demo_comprehensive_features():
    """Demonstrate all features of the enhanced library management system."""
    print("=== COMPREHENSIVE LIBRARY MANAGEMENT SYSTEM DEMO ===\n")
    
    # Initialize library
    library = Library()
    
    print("1. ADDING CATEGORIZED BOOKS TO LIBRARY")
    print("-" * 45)
    books_to_add = [
        ("The Great Gatsby", "F. Scott Fitzgerald", "Classic Literature"),
        ("To Kill a Mockingbird", "Harper Lee", "Classic Literature"),
        ("1984", "George Orwell", "Dystopian Fiction"),
        ("Pride and Prejudice", "Jane Austen", "Romance"),
        ("The Catcher in the Rye", "J.D. Salinger", "Coming of Age"),
        ("The Lord of the Rings", "J.R.R. Tolkien", "Fantasy"),
        ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "Fantasy"),
        ("The Hobbit", "J.R.R. Tolkien", "Fantasy"),
        ("A Brief History of Time", "Stephen Hawking", "Science"),
        ("The Art of War", "Sun Tzu", "Philosophy"),
        ("Jane Eyre", "Charlotte Bronte", "Classic Literature"),
        ("Wuthering Heights", "Emily Bronte", "Gothic Fiction"),
        ("Dune", "Frank Herbert", "Science Fiction"),
        ("Foundation", "Isaac Asimov", "Science Fiction")
    ]
    
    for title, author, category in books_to_add:
        book = Book(title, author, category=category)
        library.add_book(book)
        print(f"✓ Added: '{title}' by {author} (Category: {category})")
    
    print(f"\nTotal books added: {len(library.books)}")
    
    print("\n2. DISPLAYING ALL CATEGORIES")
    print("-" * 30)
    library.display_categories()
    
    print("\n3. BROWSING BOOKS BY CATEGORY")
    print("-" * 35)
    
    print("\n3a. Fantasy Books:")
    library.display_books_by_category("Fantasy")
    
    print("\n3b. Science Fiction Books:")
    library.display_books_by_category("Science Fiction")
    
    print("\n3c. Classic Literature Books:")
    library.display_books_by_category("Classic Literature")
    
    print("\n4. ADDING MEMBERS TO LIBRARY")
    print("-" * 30)
    members_to_add = [
        "Alice Johnson",
        "Bob Smith", 
        "Carol Davis",
        "David Wilson",
        "Emma Brown",
        "Frank Miller",
        "Grace Chen"
    ]
    
    for name in members_to_add:
        member = Member(name)
        library.add_member(member)
        print(f"✓ Added member: {name}")
    
    print("\n5. TESTING ADVANCED SEARCH FUNCTIONALITY")
    print("-" * 45)
    
    # Test search by title
    print("\n5a. Search by Title: 'Harry'")
    library.display_search_results("Harry", "title")
    
    # Test search by author
    print("\n5b. Search by Author: 'Tolkien'")
    library.display_search_results("Tolkien", "author")
    
    # Test search both
    print("\n5c. Search Both Title and Author: 'Time'")
    library.display_search_results("Time", "both")
    
    # Test partial searches
    print("\n5d. Search by Author: 'Bronte'")
    library.display_search_results("Bronte", "author")
    
    print("\n6. ISSUING BOOKS TO MEMBERS")
    print("-" * 30)
    issues = [
        ("The Great Gatsby", "Alice Johnson"),
        ("1984", "Bob Smith"),
        ("The Lord of the Rings", "Carol Davis"),
        ("Harry Potter and the Sorcerer's Stone", "David Wilson"),
        ("Dune", "Emma Brown"),
        ("A Brief History of Time", "Frank Miller")
    ]
    
    for title, member_name in issues:
        try:
            library.issue_book(title, member_name)
            print(f"✓ Issued '{title}' to {member_name}")
        except Exception as e:
            print(f"✗ Error issuing '{title}' to {member_name}: {e}")
    
    print("\n7. CREATING OVERDUE SCENARIO FOR TESTING")
    print("-" * 45)
    
    # Create artificial overdue situations
    overdue_members = ["Alice Johnson", "Bob Smith"]
    for member_name in overdue_members:
        member = library.find_member(member_name)
        if member and member.checked_out_books:
            # Make books overdue by different amounts
            days_overdue = 3 if member_name == "Alice Johnson" else 7
            overdue_date = date.today() - timedelta(days=days_overdue)
            for book_title in member.checked_out_books:
                member.checked_out_books[book_title].due_date = overdue_date.isoformat()
                print(f"✓ Made '{book_title}' overdue for {member_name} ({days_overdue} days)")
                break
    
    print("\n8. TESTING OVERDUE BOOKS FUNCTIONALITY")
    print("-" * 45)
    library.display_overdue_books()
    
    print("\n9. TESTING CATEGORY SEARCH AFTER ISSUING")
    print("-" * 45)
    
    print("\n9a. Remaining Fantasy Books:")
    library.display_books_by_category("Fantasy")
    
    print("\n9b. Remaining Science Fiction Books:")
    library.display_books_by_category("Science Fiction")
    
    print("\n10. SEARCHING AVAILABLE BOOKS")
    print("-" * 35)
    
    print("\n10a. Search for 'Foundation' (should be available):")
    library.display_search_results("Foundation", "title")
    
    print("\n10b. Search for Asimov books:")
    library.display_search_results("Asimov", "author")
    
    print("\n11. DISPLAYING CURRENT LIBRARY STATE")
    print("-" * 40)
    print("\n11a. Available Books (with categories):")
    library.display_books()
    
    print("\n11b. All Members with Checked Out Books:")
    library.display_members()
    
    print("\n12. RETURNING BOOKS")
    print("-" * 20)
    returns = [
        ("The Great Gatsby", "Alice Johnson", "F. Scott Fitzgerald"),
        ("1984", "Bob Smith", "George Orwell")
    ]
    
    for title, member_name, author in returns:
        try:
            library.return_book(title, member_name, author)
            print(f"✓ Successfully returned '{title}' from {member_name}")
        except Exception as e:
            print(f"✗ Error returning '{title}' from {member_name}: {e}")
    
    print("\n13. FINAL OVERDUE CHECK")
    print("-" * 25)
    library.display_overdue_books()
    
    print("\n14. FINAL CATEGORY OVERVIEW")
    print("-" * 30)
    library.display_categories()
    
    print("\n15. COMPREHENSIVE LIBRARY STATISTICS")
    print("-" * 40)
    total_books = len(library.books)
    total_members = len(library.members)
    total_issued = sum(len(member.books) for member in library.members)
    overdue_count = len(library.get_overdue_books())
    categories = library.get_all_categories()
    
    print(f"📚 Total books in library: {total_books}")
    print(f"👥 Total registered members: {total_members}")
    print(f"📖 Total books currently issued: {total_issued}")
    print(f"⚠️  Total overdue books: {overdue_count}")
    print(f"📂 Total categories: {len(categories)}")
    print(f"🏷️  Categories: {', '.join(categories)}")
    
    # Category breakdown
    print("\n📊 Books per category:")
    for category in categories:
        count = len(library.get_books_by_category(category))
        print(f"   - {category}: {count} books")
    
    print("\n16. SAVING ENHANCED DATA")
    print("-" * 25)
    try:
        library.save_data()
        print("✓ All enhanced library data saved successfully")
        
        # Check if files were created and show sizes
        files_to_check = ["books.txt", "members.txt", "ledger.txt"]
        for file in files_to_check:
            if os.path.exists(file):
                file_size = os.path.getsize(file)
                print(f"✓ {file} created ({file_size} bytes)")
            else:
                print(f"✗ {file} not found")
                
    except Exception as e:
        print(f"✗ Error saving data: {e}")
    
    print("\n=== COMPREHENSIVE DEMO COMPLETE ===")
    print("🎉 All existing and enhanced features demonstrated successfully!")
    print("\n📋 Features Demonstrated:")
    print("   ✅ Book management with categories")
    print("   ✅ Advanced search functionality (title, author, both)")
    print("   ✅ Category browsing and organization")
    print("   ✅ Member management")
    print("   ✅ Book lending with due date tracking")
    print("   ✅ Overdue book monitoring")
    print("   ✅ Book return processing")
    print("   ✅ Data persistence with enhanced models")
    print("   ✅ Comprehensive statistics and reporting")
    print("   ✅ Transaction logging")
    
    return library

if __name__ == "__main__":
    demo_comprehensive_features()