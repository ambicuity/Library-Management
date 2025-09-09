#!/usr/bin/env python3
"""
Quick population script for 50,000 books with progress tracking.
"""

import json
import random
import time
from datetime import date, timedelta

from library_management_system.library import Library
from library_management_system.models import Book, Member


def generate_books_batch(start_id, batch_size, categories, title_words, authors):
    """Generate a batch of books efficiently."""
    books = []
    
    for i in range(batch_size):
        # Simple but varied title generation
        title_parts = random.sample(title_words, random.randint(2, 4))
        title = " ".join(title_parts).title()
        
        # Random author from list
        author = random.choice(authors)
        category = random.choice(categories)
        
        book = Book(title=title, author=author, category=category)
        books.append(book)
    
    return books


def main():
    """Populate database with 50K books efficiently."""
    print("🚀 Populating database with 50,000 books...")
    
    # Initialize library
    library = Library()
    
    # Data for generation
    categories = [
        "Fiction", "Science Fiction", "Fantasy", "Mystery", "Romance", "Thriller",
        "Horror", "Adventure", "Historical Fiction", "Non-Fiction", "Biography",
        "History", "Science", "Technology", "Medicine", "Psychology", "Philosophy",
        "Self-Help", "Business", "Travel", "Art", "Music", "Poetry", "Drama",
        "Education", "Health", "Sports", "Nature", "Mathematics", "Physics",
        "Chemistry", "Biology", "Computer Science", "Engineering", "Literature"
    ]
    
    title_words = [
        "Advanced", "Ancient", "Art", "Beyond", "Black", "Blue", "Broken", "Cold",
        "Complete", "Crystal", "Dark", "Deep", "Digital", "Dragon", "Dream", "Empire",
        "Eternal", "Fire", "First", "Future", "Gold", "Great", "Green", "Guide",
        "Heart", "Hidden", "History", "Journey", "Last", "Light", "Lost", "Magic",
        "Master", "Modern", "Mystery", "Night", "Ocean", "Phoenix", "Power", "Red",
        "Royal", "Science", "Secret", "Shadow", "Silver", "Star", "Stone", "Storm",
        "Tales", "Thunder", "Time", "Tower", "Ultimate", "War", "White", "Wild",
        "Wind", "Winter", "World", "Academy", "Alliance", "Angel", "Beast", "Blood",
        "Bone", "Bridge", "Castle", "City", "Code", "Crown", "Dawn", "Death",
        "Demon", "Desert", "Diamond", "Earth", "Edge", "Element", "Energy", "Eyes",
        "Faith", "Flame", "Forest", "Freedom", "Frost", "Galaxy", "Gate", "Ghost",
        "Glass", "Glory", "Goddess", "Guardian", "Heaven", "Hero", "Hope", "Ice",
        "Iron", "Island", "Key", "King", "Knight", "Land", "Legend", "Lion",
        "Moon", "Mountain", "Oracle", "Path", "Prince", "Queen", "Quest", "Rain",
        "River", "Rose", "Sage", "Sea", "Shield", "Sky", "Soul", "Spirit",
        "Steel", "Sun", "Sword", "Temple", "Throne", "Tiger", "Tree", "Truth",
        "Valley", "Voice", "Warrior", "Water", "Wave", "Weapon", "Wisdom", "Wolf"
    ]
    
    authors = [
        "James Smith", "Mary Johnson", "John Williams", "Patricia Brown", "Robert Jones",
        "Jennifer Garcia", "Michael Miller", "Linda Davis", "William Rodriguez", "Elizabeth Martinez",
        "David Hernandez", "Barbara Lopez", "Richard Gonzalez", "Susan Wilson", "Joseph Anderson",
        "Jessica Thomas", "Thomas Taylor", "Sarah Moore", "Christopher Jackson", "Karen Martin",
        "Charles Lee", "Nancy Perez", "Daniel Thompson", "Lisa White", "Matthew Harris",
        "Betty Sanchez", "Anthony Clark", "Helen Ramirez", "Mark Lewis", "Sandra Robinson",
        "Donald Walker", "Donna Young", "Steven Allen", "Carol King", "Paul Wright",
        "Ruth Scott", "Andrew Torres", "Sharon Nguyen", "Kenneth Hill", "Michelle Flores",
        "Joshua Green", "Laura Adams", "Kevin Nelson", "Emily Baker", "Brian Hall",
        "Kimberly Rivera", "George Campbell", "Betty Mitchell", "Edward Carter", "Helen Roberts",
        "Jason Gomez", "Deborah Phillips", "Ryan Evans", "Dorothy Turner", "Jacob Diaz"
    ]
    
    print(f"📚 Starting generation of 50,000 books...")
    start_time = time.time()
    
    batch_size = 5000
    total_books = 50000
    all_books = []
    
    for batch_num in range(total_books // batch_size):
        batch_start_time = time.time()
        
        # Generate batch
        batch_books = generate_books_batch(
            batch_num * batch_size, 
            batch_size, 
            categories, 
            title_words, 
            authors
        )
        all_books.extend(batch_books)
        
        batch_time = time.time() - batch_start_time
        completed = (batch_num + 1) * batch_size
        
        print(f"   Batch {batch_num + 1}/10 complete: {completed:,}/50,000 books in {batch_time:.2f}s")
    
    # Set books in library
    library.books = all_books
    
    generation_time = time.time() - start_time
    print(f"✅ Generated 50,000 books in {generation_time:.2f} seconds")
    
    # Save to database
    print("💾 Saving to database...")
    save_start = time.time()
    library.save_data()
    save_time = time.time() - save_start
    print(f"✅ Saved to database in {save_time:.2f} seconds")
    
    # Generate some members
    print("👥 Generating 5,000 members...")
    members = []
    for i in range(5000):
        # Create unique names by adding ID suffix
        base_name = random.choice(authors)
        name = f"{base_name} (M{i+1:06d})"
        member = Member(name=name)
        members.append(member)
    
    library.members = members
    library.save_data()
    print("✅ Generated and saved 5,000 members")
    
    # Issue some books for realistic data
    print("📖 Issuing 10,000 books for realistic activity...")
    issued_count = 0
    
    for i in range(10000):
        try:
            member = random.choice(library.members)
            available_books = [book for book in library.books if book.due_date is None]
            if available_books:
                book = random.choice(available_books)
                library.issue_book(book.title, member.name)
                issued_count += 1
                
                if issued_count % 1000 == 0:
                    print(f"   Issued {issued_count:,} books...")
        except:
            continue
    
    library.save_data()
    print(f"✅ Issued {issued_count:,} books")
    
    # Quick validation
    print("\n🔍 Quick validation:")
    print(f"   Total books: {len(library.books):,}")
    print(f"   Total members: {len(library.members):,}")
    print(f"   Issued books: {sum(1 for book in library.books if book.due_date is not None):,}")
    print(f"   Categories: {len(library.get_all_categories())}")
    
    # Test search performance
    search_start = time.time()
    results = library.search_books("The", "title")
    search_time = time.time() - search_start
    print(f"   Search test: {len(results):,} results in {search_time:.3f}s")
    
    total_time = time.time() - start_time
    print(f"\n🎉 Database population complete in {total_time:.2f} seconds!")
    print("\nYou can now run: python library_management.py")


if __name__ == "__main__":
    main()