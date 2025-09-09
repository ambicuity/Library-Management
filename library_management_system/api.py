"""REST API for the Library Management System."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

try:
    from fastapi import FastAPI, HTTPException, Depends, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field
    import uvicorn

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

import json
import io

from .auth import AuthManager, User, Role, Permission
from .library import Library
from .secure_data_manager import SecureDataManager
from .models import Book, Member


# Pydantic models for API
class BookRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    category: str = Field(default="General", max_length=50)


class BookResponse(BaseModel):
    title: str
    author: str
    category: str
    due_date: Optional[str] = None
    is_available: bool


class MemberRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class MemberResponse(BaseModel):
    name: str
    books_count: int
    books: List[str]


class UserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(..., min_length=6)
    role: Role


class UserResponse(BaseModel):
    username: str
    email: str
    role: Role
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class IssueBookRequest(BaseModel):
    book_title: str
    book_author: str
    member_name: str


class ReturnBookRequest(BaseModel):
    book_title: str
    book_author: str
    member_name: str


class SearchRequest(BaseModel):
    query: str
    search_type: str = Field(default="title", regex="^(title|author|both)$")
    category: Optional[str] = None


class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"


class WebhookRequest(BaseModel):
    url: str = Field(..., regex=r"^https?://.+")
    events: List[str]
    secret: Optional[str] = None
    active: bool = True


class NotificationRequest(BaseModel):
    recipient: str
    message: str
    notification_type: str = Field(default="email", regex="^(email|sms)$")


class LibraryAPI:
    """REST API for the Library Management System."""

    def __init__(
        self,
        library: Optional[Library] = None,
        auth_manager: Optional[AuthManager] = None,
        enable_cors: bool = True,
    ):
        """Initialize the API.

        Args:
            library: Library instance to use
            auth_manager: Authentication manager to use
            enable_cors: Whether to enable CORS
        """
        if not HAS_FASTAPI:
            raise ImportError(
                "FastAPI is required for the API. Install with: pip install fastapi uvicorn"
            )

        self.app = FastAPI(
            title="Library Management System API",
            description="REST API for library management operations",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
        )

        # Initialize components
        data_manager = SecureDataManager(enable_encryption=True, enable_backups=True)
        self.library = library or Library(data_manager)
        self.auth_manager = auth_manager or AuthManager()

        # Security
        self.security = HTTPBearer()

        # CORS
        if enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],  # Configure appropriately for production
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        # Webhooks storage
        self.webhooks: List[Dict[str, Any]] = []

        # Setup routes
        self._setup_routes()

    def _get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> User:
        """Get the current authenticated user."""
        try:
            user = self.auth_manager.verify_token(credentials.credentials)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def _require_permission(self, user: User, permission: Permission) -> None:
        """Require user to have a specific permission."""
        if not user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required",
            )

    def _setup_routes(self) -> None:
        """Setup API routes."""

        # Authentication routes
        @self.app.post("/auth/login", response_model=LoginResponse)
        async def login(request: LoginRequest):
            """Authenticate user and return access token."""
            user = self.auth_manager.authenticate_user(
                request.username, request.password
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )

            try:
                access_token = self.auth_manager.create_access_token(user.username)
                return LoginResponse(
                    access_token=access_token, user=UserResponse(**user.to_dict())
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Could not create access token: {str(e)}",
                )

        @self.app.get("/auth/me", response_model=UserResponse)
        async def get_current_user_info(
            current_user: User = Depends(self._get_current_user),
        ):
            """Get current user information."""
            return UserResponse(**current_user.to_dict())

        # User management routes
        @self.app.post(
            "/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED
        )
        async def create_user(
            request: UserRequest, current_user: User = Depends(self._get_current_user)
        ):
            """Create a new user."""
            self._require_permission(current_user, Permission.ADD_MEMBERS)

            try:
                user = self.auth_manager.create_user(
                    username=request.username,
                    email=request.email,
                    password=request.password,
                    role=request.role,
                    created_by=current_user,
                )
                return UserResponse(**user.to_dict())
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )

        @self.app.get("/users", response_model=List[UserResponse])
        async def list_users(current_user: User = Depends(self._get_current_user)):
            """List all users."""
            self._require_permission(current_user, Permission.VIEW_MEMBERS)

            users = self.auth_manager.list_users(current_user)
            return [UserResponse(**user.to_dict()) for user in users]

        # Book management routes
        @self.app.get("/books", response_model=List[BookResponse])
        async def list_books(
            category: Optional[str] = None,
            current_user: User = Depends(self._get_current_user),
        ):
            """List all books or filter by category."""
            self._require_permission(current_user, Permission.VIEW_BOOKS)

            if category:
                books = self.library.filter_books_by_category(category)
            else:
                books = self.library.display_books()

            return [
                BookResponse(
                    title=book.title,
                    author=book.author,
                    category=book.category,
                    due_date=book.due_date,
                    is_available=book.due_date is None,
                )
                for book in books
            ]

        @self.app.post(
            "/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED
        )
        async def add_book(
            request: BookRequest, current_user: User = Depends(self._get_current_user)
        ):
            """Add a new book to the library."""
            self._require_permission(current_user, Permission.ADD_BOOKS)

            book = Book(
                title=request.title, author=request.author, category=request.category
            )
            self.library.add_book(book)

            return BookResponse(
                title=book.title,
                author=book.author,
                category=book.category,
                due_date=book.due_date,
                is_available=book.due_date is None,
            )

        @self.app.post("/books/search", response_model=List[BookResponse])
        async def search_books(
            request: SearchRequest, current_user: User = Depends(self._get_current_user)
        ):
            """Search for books."""
            self._require_permission(current_user, Permission.VIEW_BOOKS)

            if request.search_type == "title":
                books = self.library.search_books_by_title(request.query)
            elif request.search_type == "author":
                books = self.library.search_books_by_author(request.query)
            else:  # both
                title_books = self.library.search_books_by_title(request.query)
                author_books = self.library.search_books_by_author(request.query)
                # Combine and deduplicate
                books = list(
                    {
                        (book.title, book.author): book
                        for book in title_books + author_books
                    }.values()
                )

            return [
                BookResponse(
                    title=book.title,
                    author=book.author,
                    category=book.category,
                    due_date=book.due_date,
                    is_available=book.due_date is None,
                )
                for book in books
            ]

        # Member management routes
        @self.app.get("/members", response_model=List[MemberResponse])
        async def list_members(current_user: User = Depends(self._get_current_user)):
            """List all library members."""
            self._require_permission(current_user, Permission.VIEW_MEMBERS)

            members = self.library.display_members()
            return [
                MemberResponse(
                    name=member.name, books_count=len(member.books), books=member.books
                )
                for member in members
            ]

        @self.app.post(
            "/members",
            response_model=MemberResponse,
            status_code=status.HTTP_201_CREATED,
        )
        async def add_member(
            request: MemberRequest, current_user: User = Depends(self._get_current_user)
        ):
            """Add a new library member."""
            self._require_permission(current_user, Permission.ADD_MEMBERS)

            member = Member(name=request.name)
            self.library.add_member(member)

            return MemberResponse(
                name=member.name, books_count=len(member.books), books=member.books
            )

        # Circulation routes
        @self.app.post("/circulation/issue")
        async def issue_book(
            request: IssueBookRequest,
            current_user: User = Depends(self._get_current_user),
        ):
            """Issue a book to a member."""
            self._require_permission(current_user, Permission.ISSUE_BOOKS)

            try:
                self.library.issue_book(
                    request.book_title, request.book_author, request.member_name
                )
                return {
                    "message": f"Book '{request.book_title}' issued to {request.member_name}"
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )

        @self.app.post("/circulation/return")
        async def return_book(
            request: ReturnBookRequest,
            current_user: User = Depends(self._get_current_user),
        ):
            """Return a book from a member."""
            self._require_permission(current_user, Permission.RETURN_BOOKS)

            try:
                self.library.return_book(
                    request.book_title, request.book_author, request.member_name
                )
                return {
                    "message": f"Book '{request.book_title}' returned by {request.member_name}"
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )

        @self.app.get("/circulation/overdue")
        async def get_overdue_books(
            current_user: User = Depends(self._get_current_user),
        ):
            """Get list of overdue books."""
            self._require_permission(current_user, Permission.VIEW_OVERDUE)

            overdue_books = self.library.get_overdue_books()
            return {"overdue_books": overdue_books}

        # Export/Import routes
        @self.app.get("/export/books")
        async def export_books(
            format: ExportFormat = ExportFormat.JSON,
            current_user: User = Depends(self._get_current_user),
        ):
            """Export books data in various formats."""
            self._require_permission(current_user, Permission.VIEW_BOOKS)

            books = self.library.display_books()

            if format == ExportFormat.JSON:
                data = [
                    {
                        "title": book.title,
                        "author": book.author,
                        "category": book.category,
                        "due_date": book.due_date,
                        "is_available": book.due_date is None,
                    }
                    for book in books
                ]
                return StreamingResponse(
                    io.StringIO(json.dumps(data, indent=2)),
                    media_type="application/json",
                    headers={"Content-Disposition": "attachment; filename=books.json"},
                )

            elif format == ExportFormat.CSV:
                if not HAS_PANDAS:
                    raise HTTPException(
                        status_code=status.HTTP_501_NOT_IMPLEMENTED,
                        detail="CSV export requires pandas. Install with: pip install pandas",
                    )

                data = [
                    {
                        "title": book.title,
                        "author": book.author,
                        "category": book.category,
                        "due_date": book.due_date or "",
                        "is_available": book.due_date is None,
                    }
                    for book in books
                ]
                df = pd.DataFrame(data)
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)

                return StreamingResponse(
                    io.StringIO(csv_buffer.getvalue()),
                    media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=books.csv"},
                )

            elif format == ExportFormat.PDF:
                if not HAS_REPORTLAB:
                    raise HTTPException(
                        status_code=status.HTTP_501_NOT_IMPLEMENTED,
                        detail="PDF export requires reportlab. Install with: pip install reportlab",
                    )

                # Create PDF
                buffer = io.BytesIO()
                p = canvas.Canvas(buffer, pagesize=letter)
                width, height = letter

                # Title
                p.setFont("Helvetica-Bold", 16)
                p.drawString(72, height - 72, "Library Books Report")

                # Headers
                y = height - 120
                p.setFont("Helvetica-Bold", 10)
                p.drawString(72, y, "Title")
                p.drawString(250, y, "Author")
                p.drawString(400, y, "Category")
                p.drawString(500, y, "Status")

                # Books
                p.setFont("Helvetica", 8)
                y -= 20
                for book in books:
                    if y < 72:  # Start new page
                        p.showPage()
                        y = height - 72

                    p.drawString(
                        72,
                        y,
                        book.title[:25] + "..." if len(book.title) > 25 else book.title,
                    )
                    p.drawString(
                        250,
                        y,
                        (
                            book.author[:20] + "..."
                            if len(book.author) > 20
                            else book.author
                        ),
                    )
                    p.drawString(400, y, book.category)
                    p.drawString(
                        500, y, "Available" if book.due_date is None else "Issued"
                    )
                    y -= 15

                p.save()
                buffer.seek(0)

                return StreamingResponse(
                    io.BytesIO(buffer.getvalue()),
                    media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=books.pdf"},
                )

        # Backup routes
        @self.app.post("/backups")
        async def create_backup(current_user: User = Depends(self._get_current_user)):
            """Create a backup of the library data."""
            self._require_permission(current_user, Permission.BACKUP_RESTORE)

            backup_path = self.library.data_manager.create_backup()
            if backup_path:
                return {
                    "message": "Backup created successfully",
                    "backup_path": backup_path,
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create backup",
                )

        @self.app.get("/backups")
        async def list_backups(current_user: User = Depends(self._get_current_user)):
            """List all available backups."""
            self._require_permission(current_user, Permission.BACKUP_RESTORE)

            backups = self.library.data_manager.list_backups()
            return {"backups": backups}

        @self.app.post("/backups/{backup_name}/restore")
        async def restore_backup(
            backup_name: str, current_user: User = Depends(self._get_current_user)
        ):
            """Restore from a backup."""
            self._require_permission(current_user, Permission.BACKUP_RESTORE)

            success = self.library.data_manager.restore_backup(backup_name)
            if success:
                # Reload library data
                self.library.load_data()
                return {"message": f"Backup '{backup_name}' restored successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to restore backup '{backup_name}'",
                )

        # Webhook routes
        @self.app.post("/webhooks")
        async def create_webhook(
            request: WebhookRequest,
            current_user: User = Depends(self._get_current_user),
        ):
            """Create a new webhook."""
            self._require_permission(current_user, Permission.SYSTEM_CONFIG)

            webhook = {
                "id": len(self.webhooks) + 1,
                "url": request.url,
                "events": request.events,
                "secret": request.secret,
                "active": request.active,
                "created_at": datetime.now().isoformat(),
                "created_by": current_user.username,
            }

            self.webhooks.append(webhook)
            return webhook

        @self.app.get("/webhooks")
        async def list_webhooks(current_user: User = Depends(self._get_current_user)):
            """List all webhooks."""
            self._require_permission(current_user, Permission.SYSTEM_CONFIG)

            return {"webhooks": self.webhooks}

        # Health check
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
            }

        # Statistics
        @self.app.get("/statistics")
        async def get_statistics(current_user: User = Depends(self._get_current_user)):
            """Get library statistics."""
            self._require_permission(current_user, Permission.VIEW_BOOKS)

            stats = self.library.get_library_stats()
            return stats

    def run(
        self, host: str = "127.0.0.1", port: int = 8000, reload: bool = False
    ) -> None:
        """Run the API server.

        Args:
            host: Host to bind to
            port: Port to bind to
            reload: Enable auto-reload for development
        """
        uvicorn.run(self.app, host=host, port=port, reload=reload)


def create_api(
    library: Optional[Library] = None,
    auth_manager: Optional[AuthManager] = None,
    enable_cors: bool = True,
) -> LibraryAPI:
    """Create and configure the API instance.

    Args:
        library: Library instance to use
        auth_manager: Authentication manager to use
        enable_cors: Whether to enable CORS

    Returns:
        Configured LibraryAPI instance
    """
    return LibraryAPI(library, auth_manager, enable_cors)
