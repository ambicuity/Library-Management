"""Enhanced secure data manager for the Library Management System."""

import json
import os
import shutil
import gzip
import base64
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

from .models import Book, Member, CheckedOutBook


class EncryptionManager:
    """Handles encryption and decryption of sensitive data."""
    
    def __init__(self, password: Optional[str] = None):
        """Initialize encryption manager.
        
        Args:
            password: Password for encryption (if None, uses default)
        """
        if not HAS_CRYPTOGRAPHY:
            self.enabled = False
            return
        
        self.enabled = True
        self.password = password or "library_default_key_2024"
        self._fernet = None
    
    def _get_fernet(self) -> 'Fernet':
        """Get or create Fernet instance."""
        if self._fernet is None:
            # Derive key from password
            salt = b'salt_for_library_encryption'  # In production, use random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
            self._fernet = Fernet(key)
        return self._fernet
    
    def encrypt(self, data: str) -> str:
        """Encrypt data.
        
        Args:
            data: Plain text data
            
        Returns:
            Encrypted data as base64 string
        """
        if not self.enabled:
            return data
        
        fernet = self._get_fernet()
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data.
        
        Args:
            encrypted_data: Encrypted data as base64 string
            
        Returns:
            Decrypted plain text data
        """
        if not self.enabled:
            return encrypted_data
        
        try:
            fernet = self._get_fernet()
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception:
            # If decryption fails, assume data is not encrypted
            return encrypted_data


class BackupManager:
    """Handles automatic backups and restoration."""
    
    def __init__(self, backup_dir: str = "backups"):
        """Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, files: List[str], backup_name: Optional[str] = None) -> str:
        """Create a backup of specified files.
        
        Args:
            files: List of file paths to backup
            backup_name: Optional name for the backup (defaults to timestamp)
            
        Returns:
            Path to the created backup directory
        """
        if backup_name is None:
            backup_name = datetime.now().strftime("backup_%Y%m%d_%H%M%S")
        
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        # Copy files to backup directory
        for file_path in files:
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path / os.path.basename(file_path))
        
        # Create metadata file
        metadata = {
            "created_at": datetime.now().isoformat(),
            "files": files,
            "backup_name": backup_name,
        }
        
        with open(backup_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        return str(backup_path)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups.
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                metadata_file = backup_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        metadata["path"] = str(backup_dir)
                        backups.append(metadata)
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        return sorted(backups, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def restore_backup(self, backup_name: str, target_dir: str = ".") -> bool:
        """Restore a backup.
        
        Args:
            backup_name: Name of the backup to restore
            target_dir: Directory to restore files to
            
        Returns:
            True if restoration was successful, False otherwise
        """
        backup_path = self.backup_dir / backup_name
        metadata_file = backup_path / "metadata.json"
        
        if not metadata_file.exists():
            return False
        
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            # Restore files
            for file_name in metadata.get("files", []):
                source_file = backup_path / os.path.basename(file_name)
                target_file = os.path.join(target_dir, os.path.basename(file_name))
                
                if source_file.exists():
                    shutil.copy2(source_file, target_file)
            
            return True
        except (json.JSONDecodeError, IOError):
            return False
    
    def validate_backup(self, backup_name: str) -> bool:
        """Validate a backup's integrity.
        
        Args:
            backup_name: Name of the backup to validate
            
        Returns:
            True if backup is valid, False otherwise
        """
        backup_path = self.backup_dir / backup_name
        metadata_file = backup_path / "metadata.json"
        
        if not metadata_file.exists():
            return False
        
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            # Check if all expected files exist
            for file_name in metadata.get("files", []):
                source_file = backup_path / os.path.basename(file_name)
                if not source_file.exists():
                    return False
            
            return True
        except (json.JSONDecodeError, KeyError):
            return False


class SecureDataManager:
    """Enhanced data manager with encryption and backup capabilities."""
    
    def __init__(
        self,
        books_file: str = "books.txt",
        members_file: str = "members.txt",
        ledger_file: str = "ledger.txt",
        enable_encryption: bool = False,
        encryption_password: Optional[str] = None,
        enable_backups: bool = True,
    ):
        """Initialize the secure data manager.
        
        Args:
            books_file: Path to the books data file
            members_file: Path to the members data file
            ledger_file: Path to the transaction ledger file
            enable_encryption: Whether to enable encryption
            encryption_password: Password for encryption
            enable_backups: Whether to enable automatic backups
        """
        self.books_file = books_file
        self.members_file = members_file
        self.ledger_file = ledger_file
        
        self.encryption = EncryptionManager(encryption_password) if enable_encryption else None
        self.backup_manager = BackupManager() if enable_backups else None
        
        # Configuration
        self.auto_backup_interval = 24  # hours
        self.max_backups = 30  # keep last 30 backups
    
    def _compress_data(self, data: str) -> bytes:
        """Compress data using gzip.
        
        Args:
            data: Data to compress
            
        Returns:
            Compressed data
        """
        return gzip.compress(data.encode('utf-8'))
    
    def _decompress_data(self, compressed_data: bytes) -> str:
        """Decompress gzipped data.
        
        Args:
            compressed_data: Compressed data
            
        Returns:
            Decompressed data
        """
        return gzip.decompress(compressed_data).decode('utf-8')
    
    def _read_secure_file(self, file_path: str) -> str:
        """Read and decrypt a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Decrypted file contents
        """
        if not os.path.exists(file_path):
            return "{}"  # Return empty JSON
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Try to decrypt if encryption is enabled
        if self.encryption and self.encryption.enabled:
            try:
                content = self.encryption.decrypt(content)
            except Exception:
                # If decryption fails, assume file is not encrypted
                pass
        
        return content
    
    def _write_secure_file(self, file_path: str, content: str) -> None:
        """Encrypt and write content to a file.
        
        Args:
            file_path: Path to the file
            content: Content to write
        """
        # Encrypt if encryption is enabled
        if self.encryption and self.encryption.enabled:
            content = self.encryption.encrypt(content)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def create_backup(self, backup_name: Optional[str] = None) -> Optional[str]:
        """Create a backup of all data files.
        
        Args:
            backup_name: Optional name for the backup
            
        Returns:
            Path to created backup, or None if backups are disabled
        """
        if not self.backup_manager:
            return None
        
        files = [self.books_file, self.members_file, self.ledger_file]
        return self.backup_manager.create_backup(files, backup_name)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups.
        
        Returns:
            List of backup information dictionaries
        """
        if not self.backup_manager:
            return []
        
        return self.backup_manager.list_backups()
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore from a backup.
        
        Args:
            backup_name: Name of the backup to restore
            
        Returns:
            True if restoration was successful, False otherwise
        """
        if not self.backup_manager:
            return False
        
        return self.backup_manager.restore_backup(backup_name)
    
    def load_books(self) -> List[Book]:
        """Load books from the data file.
        
        Returns:
            List of Book objects
        """
        try:
            content = self._read_secure_file(self.books_file)
            books_data = json.loads(content)
            
            books = []
            for book_dict in books_data:
                if not isinstance(book_dict, dict):
                    continue
                if "title" not in book_dict or "author" not in book_dict:
                    continue
                
                book = Book(
                    title=book_dict["title"],
                    author=book_dict["author"],
                    due_date=book_dict.get("due_date"),
                    category=book_dict.get("category", "General")
                )
                books.append(book)
            
            return books
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # Create backup before returning empty list
            if self.backup_manager and os.path.exists(self.books_file):
                self.create_backup(f"corrupt_books_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            raise ValueError(f"Error loading books data: {e}")
    
    def save_books(self, books: List[Book]) -> None:
        """Save books to the data file.
        
        Args:
            books: List of Book objects to save
        """
        try:
            # Create backup before saving
            if self.backup_manager and os.path.exists(self.books_file):
                self.create_backup()
            
            books_data = []
            for book in books:
                book_dict = {
                    "title": book.title,
                    "author": book.author,
                    "due_date": book.due_date,
                    "category": book.category
                }
                books_data.append(book_dict)
            
            content = json.dumps(books_data, indent=2)
            self._write_secure_file(self.books_file, content)
            
        except IOError as e:
            raise IOError(f"Error saving books data: {e}")
    
    def load_members(self) -> List[Member]:
        """Load members from the data file.
        
        Returns:
            List of Member objects
        """
        try:
            content = self._read_secure_file(self.members_file)
            members_data = json.loads(content)
            
            members = []
            for member_dict in members_data:
                if not isinstance(member_dict, dict):
                    continue
                if "name" not in member_dict:
                    continue
                
                member = Member(
                    name=member_dict["name"], 
                    books=member_dict.get("books", [])
                )
                
                # Load checked out books if they exist
                if "checked_out_books" in member_dict:
                    for title, book_data in member_dict["checked_out_books"].items():
                        if isinstance(book_data, dict) and all(k in book_data for k in ["title", "author", "due_date"]):
                            member.checked_out_books[title] = CheckedOutBook(
                                title=book_data["title"],
                                author=book_data["author"],
                                due_date=book_data["due_date"]
                            )
                
                members.append(member)
            return members
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # Create backup before returning empty list
            if self.backup_manager and os.path.exists(self.members_file):
                self.create_backup(f"corrupt_members_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            raise ValueError(f"Error loading members data: {e}")
    
    def save_members(self, members: List[Member]) -> None:
        """Save members to the data file.
        
        Args:
            members: List of Member objects to save
        """
        try:
            # Create backup before saving
            if self.backup_manager and os.path.exists(self.members_file):
                self.create_backup()
            
            members_data = []
            for member in members:
                member_dict = {
                    "name": member.name,
                    "books": member.books,
                    "checked_out_books": {}
                }
                # Convert CheckedOutBook objects to dictionaries
                for title, checked_out_book in member.checked_out_books.items():
                    member_dict["checked_out_books"][title] = {
                        "title": checked_out_book.title,
                        "author": checked_out_book.author,
                        "due_date": checked_out_book.due_date
                    }
                members_data.append(member_dict)
            
            content = json.dumps(members_data, indent=2)
            self._write_secure_file(self.members_file, content)
            
        except IOError as e:
            raise IOError(f"Error saving members data: {e}")
    
    def log_transaction(self, transaction: str) -> None:
        """Log a transaction to the ledger.
        
        Args:
            transaction: Transaction description
        """
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] {transaction}\n"
            
            # Append to encrypted log file
            if self.encryption and self.encryption.enabled:
                # Read existing content
                existing_content = ""
                if os.path.exists(self.ledger_file):
                    existing_content = self._read_secure_file(self.ledger_file)
                
                # Append new entry
                new_content = existing_content + log_entry
                self._write_secure_file(self.ledger_file, new_content)
            else:
                # Append to regular file
                with open(self.ledger_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                    
        except IOError as e:
            print(f"Warning: Could not log transaction: {e}")
    
    def get_transaction_log(self, limit: Optional[int] = None) -> List[str]:
        """Get transaction log entries.
        
        Args:
            limit: Maximum number of entries to return (None for all)
            
        Returns:
            List of log entries
        """
        try:
            content = self._read_secure_file(self.ledger_file)
            entries = [line.strip() for line in content.split('\n') if line.strip()]
            
            if limit:
                entries = entries[-limit:]
            
            return entries
        except (FileNotFoundError, IOError):
            return []