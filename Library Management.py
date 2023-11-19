import datetime
import json

class Book:
    def __init__(self, title, author, due_date=None):
        self.title = title
        self.author = author
        self.due_date = due_date

class Member:
    def __init__(self, name, books=None):
        self.name = name
        self.books = books if books else []

class Library:
    def __init__(self):
        self.books = []
        self.members = []

    def load_data(self):
        try:
            with open('books.txt', 'r') as f:
                books_json = json.load(f)
                for book in books_json:
                    self.books.append(Book(book['title'], book['author'], book['due_date']))

            with open('members.txt', 'r') as f:
                members_json = json.load(f)
                for member in members_json:
                    self.members.append(Member(member['name'], member['books']))
        except FileNotFoundError:
            pass

    def save_data(self):
        with open('books.txt', 'w') as f:
            json.dump([book.__dict__ for book in self.books], f)

        with open('members.txt', 'w') as f:
            json.dump([member.__dict__ for member in self.members], f)

    def add_book(self, book):
        self.books.append(book)

    def add_member(self, member):
        self.members.append(member)

    def issue_book(self, title, member_name):
        for book in self.books:
            if book.title == title:
                for member in self.members:
                    if member.name == member_name:
                        self.books.remove(book)
                        book.due_date = str(datetime.date.today() + datetime.timedelta(days=14))
                        member.books.append(book.title)
                        with open('ledger.txt', 'a') as f:
                            f.write(f'{datetime.datetime.now()} - Issued "{title}" to {member_name}\n')
                        return True
        return False

    def return_book(self, title, member_name):
        for member in self.members:
            if member.name == member_name:
                if title in member.books:
                    member.books.remove(title)
                    book = Book(title, 'Unknown', None)
                    self.books.append(book)
                    with open('ledger.txt', 'a') as f:
                        f.write(f'{datetime.datetime.now()} - Returned "{title}" from {member_name}\n')
                    return True
        return False

    def display_books(self):
        for book in self.books:
            print(f'Title: {book.title}, Author: {book.author}, Due date: {book.due_date}')

def main():
    library = Library()
    library.load_data()
    while True:
        print('1. Add book')
        print('2. Add member')
        print('3. Issue book')
        print('4. Return book')
        print('5. Display all books')
        print('6. Quit')
        choice = int(input('Enter your choice: '))
        if choice == 1:
            title = input('Enter book title: ')
            author = input('Enter book author: ')
            library.add_book(Book(title, author))
        elif choice == 2:
            name = input('Enter member name: ')
            library.add_member(Member(name))
        elif choice == 3:
            title = input('Enter book title to issue: ')
            member_name = input('Enter member name: ')
            if library.issue_book(title, member_name):
                print('Book issued successfully')
            else:
                print('Book is not available or member does not exist')
        elif choice == 4:
            title = input('Enter book title to return: ')
            member_name = input('Enter member name: ')
            if library.return_book(title, member_name):
                print('Book returned successfully')
            else:
                print('Book or member does not exist')
        elif choice == 5:
            library.display_books()
        elif choice == 6:
            library.save_data()
            break

if __name__ == '__main__':
    main()