"""Authentication and authorization module for the Library Management System."""

import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum

try:
    from passlib.context import CryptContext
    from passlib.hash import bcrypt
    HAS_PASSLIB = True
except ImportError:
    HAS_PASSLIB = False

try:
    from jose import JWTError, jwt
    HAS_JOSE = True
except ImportError:
    HAS_JOSE = False


class Role(Enum):
    """User roles for the library system."""
    
    MEMBER = "member"
    LIBRARIAN = "librarian"
    ADMIN = "admin"


class Permission(Enum):
    """Permissions for different operations."""
    
    # Book operations
    VIEW_BOOKS = "view_books"
    ADD_BOOKS = "add_books"
    EDIT_BOOKS = "edit_books"
    DELETE_BOOKS = "delete_books"
    
    # Member operations
    VIEW_MEMBERS = "view_members"
    ADD_MEMBERS = "add_members"
    EDIT_MEMBERS = "edit_members"
    DELETE_MEMBERS = "delete_members"
    
    # Library operations
    ISSUE_BOOKS = "issue_books"
    RETURN_BOOKS = "return_books"
    VIEW_OVERDUE = "view_overdue"
    
    # System operations
    BACKUP_RESTORE = "backup_restore"
    VIEW_LOGS = "view_logs"
    SYSTEM_CONFIG = "system_config"


# Role-permission mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.MEMBER: {
        Permission.VIEW_BOOKS,
        Permission.RETURN_BOOKS,  # Members can return their own books
    },
    Role.LIBRARIAN: {
        Permission.VIEW_BOOKS,
        Permission.ADD_BOOKS,
        Permission.EDIT_BOOKS,
        Permission.VIEW_MEMBERS,
        Permission.ADD_MEMBERS,
        Permission.ISSUE_BOOKS,
        Permission.RETURN_BOOKS,
        Permission.VIEW_OVERDUE,
    },
    Role.ADMIN: set(Permission),  # Admin has all permissions
}


class User:
    """Represents a system user with authentication and authorization."""
    
    def __init__(
        self,
        username: str,
        email: str,
        role: Role,
        password_hash: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
    ):
        """Initialize a new user.
        
        Args:
            username: Unique username
            email: User's email address
            role: User's role in the system
            password_hash: Hashed password
            is_active: Whether the user account is active
            created_at: When the user was created
            last_login: Last login timestamp
        """
        self.username = username
        self.email = email
        self.role = role
        self.password_hash = password_hash
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
        self.last_login = last_login
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission.
        
        Args:
            permission: The permission to check
            
        Returns:
            True if user has the permission, False otherwise
        """
        if not self.is_active:
            return False
        return permission in ROLE_PERMISSIONS.get(self.role, set())
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary for serialization."""
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "password_hash": self.password_hash,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "User":
        """Create user from dictionary."""
        return cls(
            username=data["username"],
            email=data["email"],
            role=Role(data["role"]),
            password_hash=data.get("password_hash"),
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None,
        )


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthorizationError(Exception):
    """Raised when user lacks required permissions."""
    pass


class AuthManager:
    """Manages user authentication and authorization."""
    
    def __init__(self, users_file: str = "users.json", secret_key: Optional[str] = None):
        """Initialize the authentication manager.
        
        Args:
            users_file: Path to the users data file
            secret_key: Secret key for JWT tokens
        """
        self.users_file = users_file
        self.secret_key = secret_key or self._generate_secret_key()
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # Initialize password context if passlib is available
        if HAS_PASSLIB:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        else:
            self.pwd_context = None
        
        self.users: Dict[str, User] = {}
        self.load_users()
        
        # Create default admin user if no users exist
        if not self.users:
            self._create_default_admin()
    
    def _generate_secret_key(self) -> str:
        """Generate a random secret key for JWT tokens."""
        return secrets.token_urlsafe(32)
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt or fallback to SHA-256."""
        if self.pwd_context:
            return self.pwd_context.hash(password)
        else:
            # Fallback to SHA-256 with salt
            salt = secrets.token_bytes(32)
            return hashlib.sha256(salt + password.encode()).hexdigest() + ":" + salt.hex()
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        if self.pwd_context:
            return self.pwd_context.verify(plain_password, hashed_password)
        else:
            # Fallback verification
            try:
                hash_part, salt_part = hashed_password.split(":")
                salt = bytes.fromhex(salt_part)
                return hashlib.sha256(salt + plain_password.encode()).hexdigest() == hash_part
            except ValueError:
                return False
    
    def _create_default_admin(self) -> None:
        """Create a default admin user."""
        admin_user = User(
            username="admin",
            email="admin@library.local",
            role=Role.ADMIN,
            password_hash=self._hash_password("admin123"),  # Default password
        )
        self.users["admin"] = admin_user
        self.save_users()
    
    def load_users(self) -> None:
        """Load users from the data file."""
        if not os.path.exists(self.users_file):
            return
        
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                users_data = json.load(f)
                self.users = {
                    username: User.from_dict(user_data)
                    for username, user_data in users_data.items()
                }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Could not load users data: {e}")
            self.users = {}
    
    def save_users(self) -> None:
        """Save users to the data file."""
        users_data = {
            username: user.to_dict()
            for username, user in self.users.items()
        }
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(users_data, f, indent=2)
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: Role,
        created_by: Optional[User] = None,
    ) -> User:
        """Create a new user.
        
        Args:
            username: Unique username
            email: User's email
            password: Plain text password
            role: User's role
            created_by: User creating this user (for permission check)
            
        Returns:
            The created user
            
        Raises:
            ValueError: If username already exists
            AuthorizationError: If creator lacks permission
        """
        if created_by and not created_by.has_permission(Permission.ADD_MEMBERS):
            raise AuthorizationError("Insufficient permissions to create users")
        
        if username in self.users:
            raise ValueError(f"Username '{username}' already exists")
        
        user = User(
            username=username,
            email=email,
            role=role,
            password_hash=self._hash_password(password),
        )
        
        self.users[username] = user
        self.save_users()
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.users.get(username)
        if not user or not user.is_active:
            return None
        
        if not user.password_hash or not self._verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.now()
        self.save_users()
        return user
    
    def create_access_token(self, username: str) -> str:
        """Create a JWT access token for a user.
        
        Args:
            username: Username
            
        Returns:
            JWT access token
            
        Raises:
            AuthenticationError: If JWT library not available
        """
        if not HAS_JOSE:
            raise AuthenticationError("JWT functionality not available. Install python-jose.")
        
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {"sub": username, "exp": expire}
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[User]:
        """Verify and decode a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            User object if token is valid, None otherwise
        """
        if not HAS_JOSE:
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return self.users.get(username)
        except JWTError:
            return None
    
    def require_permission(self, user: Optional[User], permission: Permission) -> None:
        """Require a user to have a specific permission.
        
        Args:
            user: User to check
            permission: Required permission
            
        Raises:
            AuthenticationError: If user is None
            AuthorizationError: If user lacks permission
        """
        if user is None:
            raise AuthenticationError("Authentication required")
        
        if not user.has_permission(permission):
            raise AuthorizationError(f"Permission '{permission.value}' required")
    
    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username.
        
        Args:
            username: Username to look up
            
        Returns:
            User object if found, None otherwise
        """
        return self.users.get(username)
    
    def list_users(self, requesting_user: Optional[User] = None) -> List[User]:
        """List all users.
        
        Args:
            requesting_user: User making the request
            
        Returns:
            List of users
            
        Raises:
            AuthorizationError: If user lacks permission
        """
        if requesting_user:
            self.require_permission(requesting_user, Permission.VIEW_MEMBERS)
        
        return list(self.users.values())
    
    def update_user(
        self,
        username: str,
        updates: Dict,
        updating_user: Optional[User] = None,
    ) -> User:
        """Update a user's information.
        
        Args:
            username: Username to update
            updates: Dictionary of fields to update
            updating_user: User making the update
            
        Returns:
            Updated user
            
        Raises:
            ValueError: If user not found
            AuthorizationError: If user lacks permission
        """
        if updating_user:
            self.require_permission(updating_user, Permission.EDIT_MEMBERS)
        
        user = self.users.get(username)
        if not user:
            raise ValueError(f"User '{username}' not found")
        
        # Update allowed fields
        if "email" in updates:
            user.email = updates["email"]
        if "role" in updates and isinstance(updates["role"], Role):
            user.role = updates["role"]
        if "is_active" in updates:
            user.is_active = updates["is_active"]
        if "password" in updates:
            user.password_hash = self._hash_password(updates["password"])
        
        self.save_users()
        return user
    
    def delete_user(self, username: str, deleting_user: Optional[User] = None) -> bool:
        """Delete a user.
        
        Args:
            username: Username to delete
            deleting_user: User making the deletion
            
        Returns:
            True if user was deleted, False if not found
            
        Raises:
            AuthorizationError: If user lacks permission
            ValueError: If trying to delete self or last admin
        """
        if deleting_user:
            self.require_permission(deleting_user, Permission.DELETE_MEMBERS)
            
            if deleting_user.username == username:
                raise ValueError("Cannot delete your own account")
        
        user = self.users.get(username)
        if not user:
            return False
        
        # Prevent deletion of last admin
        admin_count = sum(1 for u in self.users.values() if u.role == Role.ADMIN and u.is_active)
        if user.role == Role.ADMIN and admin_count <= 1:
            raise ValueError("Cannot delete the last active admin user")
        
        del self.users[username]
        self.save_users()
        return True