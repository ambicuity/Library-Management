#!/usr/bin/env python3
"""
Enhanced Library Management System

A comprehensive library management system with advanced features including:
- Role-based access control (RBAC)
- Enhanced encryption for data storage
- Automatic backup scheduling
- REST API for external integrations
- Export/import functionality (CSV, JSON, PDF)
- Webhooks for real-time notifications
- Search autocomplete and fuzzy suggestions
- Dark mode / theming support
- Multi-language support (internationalization)
- Accessibility compliance
- Automated email/SMS reminders
- Admin dashboard alerts
- CI/CD pipeline support
- Comprehensive logging and monitoring

Usage:
    # CLI Mode (default)
    python library_management.py
    
    # API Server Mode
    python library_management.py --mode api
    
    # Web Interface Mode
    python library_management.py --mode web
    
    # Combined Mode (API + Web)
    python library_management.py --mode combined
    
    # Help
    python library_management.py --help
"""

import argparse
import sys
import os
from pathlib import Path

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, str(Path(__file__).parent))

from library_management_system.cli import CLI
from library_management_system.library import Library
from library_management_system.secure_data_manager import SecureDataManager
from library_management_system.auth import AuthManager, Role
from library_management_system.monitoring import MonitoringSystem
from library_management_system.i18n import init_i18n


def setup_system(enable_encryption: bool = True, enable_monitoring: bool = True) -> tuple:
    """Setup the enhanced library management system.
    
    Args:
        enable_encryption: Whether to enable data encryption
        enable_monitoring: Whether to enable monitoring
        
    Returns:
        Tuple of (library, auth_manager, monitoring_system)
    """
    # Initialize internationalization
    i18n = init_i18n(default_language="en", translations_dir="translations")
    
    # Initialize secure data manager
    data_manager = SecureDataManager(
        enable_encryption=enable_encryption,
        enable_backups=True
    )
    
    # Initialize authentication manager
    auth_manager = AuthManager()
    
    # Create default admin user if no users exist
    if not auth_manager.users:
        print("Creating default admin user...")
        admin_user = auth_manager.create_user(
            username="admin",
            email="admin@library.local",
            password="admin123",  # Default password - should be changed in production
            role=Role.ADMIN
        )
        print(f"Default admin user created: {admin_user.username}/admin123")
        print("⚠️  Please change the default password in production!")
    
    # Initialize library with secure data manager
    library = Library(data_manager)
    
    # Initialize monitoring system
    monitoring_system = None
    if enable_monitoring:
        monitoring_system = MonitoringSystem(
            enable_performance_monitoring=True,
            enable_security_monitoring=True
        )
        
        # Record system startup
        monitoring_system.record_system_event(
            "system_startup",
            "Library Management System started successfully"
        )
    
    return library, auth_manager, monitoring_system


def run_cli_mode(library: Library, auth_manager: AuthManager, monitoring_system=None) -> None:
    """Run the CLI interface.
    
    Args:
        library: Library instance
        auth_manager: Authentication manager
        monitoring_system: Monitoring system (optional)
    """
    print("🚀 Starting Enhanced Library Management System (CLI Mode)")
    print("=" * 60)
    
    # Enhanced CLI with authentication
    cli = CLI(
        library=library,
        auth_manager=auth_manager,
        monitoring_system=monitoring_system
    )
    cli.run()


def run_api_mode(library: Library, auth_manager: AuthManager, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the API server.
    
    Args:
        library: Library instance
        auth_manager: Authentication manager
        host: Host to bind to
        port: Port to bind to
    """
    try:
        from library_management_system.api import create_api
        
        print("🚀 Starting Enhanced Library Management System (API Mode)")
        print("=" * 60)
        print(f"API server will be available at: http://{host}:{port}")
        print(f"API documentation will be available at: http://{host}:{port}/docs")
        print("Press Ctrl+C to stop the server")
        print()
        
        # Create and run API
        api = create_api(library=library, auth_manager=auth_manager)
        api.run(host=host, port=port)
        
    except ImportError as e:
        print(f"❌ Error: Cannot start API mode - {e}")
        print("💡 Install required dependencies: pip install fastapi uvicorn")
        sys.exit(1)


def run_web_mode(library: Library, auth_manager: AuthManager, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the web interface.
    
    Args:
        library: Library instance
        auth_manager: Authentication manager
        host: Host to bind to
        port: Port to bind to
    """
    try:
        from library_management_system.web_interface import create_web_interface
        
        print("🚀 Starting Enhanced Library Management System (Web Mode)")
        print("=" * 60)
        print(f"Web interface will be available at: http://{host}:{port}")
        print("Press Ctrl+C to stop the server")
        print()
        
        # Create and run web interface
        web = create_web_interface(library=library, auth_manager=auth_manager)
        web.run(host=host, port=port)
        
    except ImportError as e:
        print(f"❌ Error: Cannot start web mode - {e}")
        print("💡 Install required dependencies: pip install fastapi uvicorn jinja2")
        sys.exit(1)


def run_combined_mode(library: Library, auth_manager: AuthManager, host: str = "127.0.0.1") -> None:
    """Run both API and web interface.
    
    Args:
        library: Library instance
        auth_manager: Authentication manager
        host: Host to bind to
    """
    import threading
    import time
    
    try:
        from library_management_system.api import create_api
        from library_management_system.web_interface import create_web_interface
        
        print("🚀 Starting Enhanced Library Management System (Combined Mode)")
        print("=" * 60)
        print(f"API server will be available at: http://{host}:8000")
        print(f"API documentation will be available at: http://{host}:8000/docs")
        print(f"Web interface will be available at: http://{host}:8080")
        print("Press Ctrl+C to stop both servers")
        print()
        
        # Start API server in a separate thread
        api = create_api(library=library, auth_manager=auth_manager)
        api_thread = threading.Thread(
            target=lambda: api.run(host=host, port=8000, reload=False),
            daemon=True
        )
        api_thread.start()
        
        # Give API server time to start
        time.sleep(2)
        
        # Start web interface on main thread
        web = create_web_interface(library=library, auth_manager=auth_manager)
        web.run(host=host, port=8080, reload=False)
        
    except ImportError as e:
        print(f"❌ Error: Cannot start combined mode - {e}")
        print("💡 Install required dependencies: pip install fastapi uvicorn jinja2")
        sys.exit(1)


def main() -> None:
    """Main entry point for the Enhanced Library Management System."""
    parser = argparse.ArgumentParser(
        description="Enhanced Library Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python library_management.py                    # Start CLI mode
  python library_management.py --mode api         # Start API server
  python library_management.py --mode web         # Start web interface
  python library_management.py --mode combined    # Start API + Web
  python library_management.py --mode api --port 9000  # Custom port
  python library_management.py --no-encryption    # Disable encryption
  python library_management.py --no-monitoring    # Disable monitoring
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["cli", "api", "web", "combined"],
        default="cli",
        help="Mode to run the system in (default: cli)"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for server modes (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for server modes (default: 8000)"
    )
    
    parser.add_argument(
        "--no-encryption",
        action="store_true",
        help="Disable data encryption"
    )
    
    parser.add_argument(
        "--no-monitoring",
        action="store_true",
        help="Disable monitoring and logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Enhanced Library Management System v2.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        # Setup the system
        library, auth_manager, monitoring_system = setup_system(
            enable_encryption=not args.no_encryption,
            enable_monitoring=not args.no_monitoring
        )
        
        # Run in the specified mode
        if args.mode == "cli":
            run_cli_mode(library, auth_manager, monitoring_system)
        elif args.mode == "api":
            run_api_mode(library, auth_manager, args.host, args.port)
        elif args.mode == "web":
            run_web_mode(library, auth_manager, args.host, args.port)
        elif args.mode == "combined":
            run_combined_mode(library, auth_manager, args.host)
        
    except KeyboardInterrupt:
        print("\n")
        print("👋 Library Management System stopped")
        
        # Record system shutdown
        if monitoring_system:
            monitoring_system.record_system_event(
                "system_shutdown",
                "Library Management System stopped by user"
            )
            monitoring_system.shutdown()
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        
        # Record system error
        if 'monitoring_system' in locals() and monitoring_system:
            monitoring_system.record_system_event(
                "system_error",
                f"Fatal error occurred: {e}",
                level="ERROR"
            )
            monitoring_system.shutdown()
        
        sys.exit(1)


if __name__ == "__main__":
    main()
