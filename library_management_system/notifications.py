"""Notification system for the Library Management System."""

import smtplib
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dataclasses import dataclass
from enum import Enum

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import schedule

    HAS_SCHEDULE = True
except ImportError:
    HAS_SCHEDULE = False


class NotificationType(Enum):
    """Types of notifications."""

    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"


class NotificationPriority(Enum):
    """Notification priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationTemplate:
    """Template for notifications."""

    name: str
    subject: str
    body: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL


@dataclass
class NotificationRecipient:
    """Notification recipient information."""

    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_method: NotificationType = NotificationType.EMAIL


@dataclass
class Notification:
    """Individual notification."""

    id: str
    recipient: NotificationRecipient
    template: NotificationTemplate
    data: Dict[str, Any]
    scheduled_time: Optional[datetime] = None
    sent_time: Optional[datetime] = None
    status: str = "pending"  # pending, sent, failed, cancelled
    error_message: Optional[str] = None


class EmailNotificationService:
    """Email notification service."""

    def __init__(
        self,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        """Initialize email service.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            from_email: From email address
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username or os.getenv("SMTP_USERNAME")
        self.password = password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or self.username

        self.enabled = bool(self.username and self.password)

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
    ) -> bool:
        """Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            attachments: List of file paths to attach

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            print("Email service not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject

            # Add plain text part
            text_part = MIMEText(body, "plain")
            msg.attach(text_part)

            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                msg.attach(html_part)

            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(file_path)}",
                        )
                        msg.attach(part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False


class SMSNotificationService:
    """SMS notification service using webhook."""

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize SMS service.

        Args:
            api_url: SMS API endpoint URL
            api_key: SMS API key
        """
        self.api_url = api_url or os.getenv("SMS_API_URL")
        self.api_key = api_key or os.getenv("SMS_API_KEY")
        self.enabled = bool(self.api_url and self.api_key and HAS_REQUESTS)

    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send an SMS message.

        Args:
            phone_number: Recipient phone number
            message: SMS message text

        Returns:
            True if SMS was sent successfully, False otherwise
        """
        if not self.enabled:
            print("SMS service not configured or requests library not available")
            return False

        try:
            # Generic SMS API call - adjust based on your SMS provider
            payload = {
                "to": phone_number,
                "message": message,
                "api_key": self.api_key,
            }

            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()

            return True

        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False


class WebhookNotificationService:
    """Webhook notification service."""

    def __init__(self):
        """Initialize webhook service."""
        self.enabled = HAS_REQUESTS

    def send_webhook(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None,
    ) -> bool:
        """Send a webhook notification.

        Args:
            url: Webhook URL
            payload: Payload to send
            headers: Additional headers
            secret: Webhook secret for signature

        Returns:
            True if webhook was sent successfully, False otherwise
        """
        if not self.enabled:
            print("Webhook service not available - requests library not found")
            return False

        try:
            # Prepare headers
            request_headers = {"Content-Type": "application/json"}
            if headers:
                request_headers.update(headers)

            # Add timestamp and signature if secret provided
            if secret:
                import hmac
                import hashlib

                payload["timestamp"] = datetime.now().isoformat()
                payload_str = json.dumps(payload, sort_keys=True)
                signature = hmac.new(
                    secret.encode(), payload_str.encode(), hashlib.sha256
                ).hexdigest()
                request_headers["X-Webhook-Signature"] = f"sha256={signature}"

            # Send webhook
            response = requests.post(
                url, json=payload, headers=request_headers, timeout=30
            )
            response.raise_for_status()

            return True

        except Exception as e:
            print(f"Failed to send webhook: {e}")
            return False


class NotificationManager:
    """Manages all types of notifications."""

    def __init__(
        self,
        email_service: Optional[EmailNotificationService] = None,
        sms_service: Optional[SMSNotificationService] = None,
        webhook_service: Optional[WebhookNotificationService] = None,
    ):
        """Initialize notification manager.

        Args:
            email_service: Email notification service
            sms_service: SMS notification service
            webhook_service: Webhook notification service
        """
        self.email_service = email_service or EmailNotificationService()
        self.sms_service = sms_service or SMSNotificationService()
        self.webhook_service = webhook_service or WebhookNotificationService()

        # Load templates and recipients
        self.templates: Dict[str, NotificationTemplate] = {}
        self.recipients: Dict[str, NotificationRecipient] = {}
        self.notifications: List[Notification] = []

        # Webhook endpoints
        self.webhooks: List[Dict[str, Any]] = []

        self._load_templates()
        self._load_recipients()

    def _load_templates(self) -> None:
        """Load notification templates."""
        # Default templates
        self.templates = {
            "book_due": NotificationTemplate(
                name="book_due",
                subject="Book Due Reminder - {title}",
                body="Dear {member_name},\n\nThis is a reminder that the book '{title}' by {author} is due on {due_date}.\n\nPlease return it to avoid any late fees.\n\nThank you,\nLibrary Management System",
                notification_type=NotificationType.EMAIL,
                priority=NotificationPriority.NORMAL,
            ),
            "book_overdue": NotificationTemplate(
                name="book_overdue",
                subject="Overdue Book Notice - {title}",
                body="Dear {member_name},\n\nThe book '{title}' by {author} was due on {due_date} and is now overdue by {days_overdue} days.\n\nPlease return it immediately to avoid additional charges.\n\nThank you,\nLibrary Management System",
                notification_type=NotificationType.EMAIL,
                priority=NotificationPriority.HIGH,
            ),
            "book_reserved": NotificationTemplate(
                name="book_reserved",
                subject="Book Available - {title}",
                body="Dear {member_name},\n\nThe book '{title}' by {author} that you reserved is now available for pickup.\n\nPlease collect it within 3 days.\n\nThank you,\nLibrary Management System",
                notification_type=NotificationType.EMAIL,
                priority=NotificationPriority.NORMAL,
            ),
            "system_alert": NotificationTemplate(
                name="system_alert",
                subject="System Alert - {alert_type}",
                body="System Alert: {message}\n\nTime: {timestamp}\nSeverity: {severity}\n\nLibrary Management System",
                notification_type=NotificationType.EMAIL,
                priority=NotificationPriority.URGENT,
            ),
        }

    def _load_recipients(self) -> None:
        """Load notification recipients from file."""
        recipients_file = "notification_recipients.json"

        if os.path.exists(recipients_file):
            try:
                with open(recipients_file, "r") as f:
                    data = json.load(f)

                for name, recipient_data in data.items():
                    self.recipients[name] = NotificationRecipient(
                        name=recipient_data["name"],
                        email=recipient_data.get("email"),
                        phone=recipient_data.get("phone"),
                        preferred_method=NotificationType(
                            recipient_data.get("preferred_method", "email")
                        ),
                    )
            except (json.JSONDecodeError, KeyError, ValueError):
                print("Warning: Could not load notification recipients")

    def save_recipients(self) -> None:
        """Save notification recipients to file."""
        recipients_file = "notification_recipients.json"

        data = {}
        for name, recipient in self.recipients.items():
            data[name] = {
                "name": recipient.name,
                "email": recipient.email,
                "phone": recipient.phone,
                "preferred_method": recipient.preferred_method.value,
            }

        with open(recipients_file, "w") as f:
            json.dump(data, f, indent=2)

    def add_recipient(self, recipient: NotificationRecipient) -> None:
        """Add a notification recipient.

        Args:
            recipient: Notification recipient to add
        """
        self.recipients[recipient.name] = recipient
        self.save_recipients()

    def add_webhook(
        self, url: str, events: List[str], secret: Optional[str] = None
    ) -> None:
        """Add a webhook endpoint.

        Args:
            url: Webhook URL
            events: List of events to send to this webhook
            secret: Optional webhook secret
        """
        webhook = {
            "url": url,
            "events": events,
            "secret": secret,
            "active": True,
            "created_at": datetime.now().isoformat(),
        }
        self.webhooks.append(webhook)

    def send_notification(
        self,
        template_name: str,
        recipient_name: str,
        data: Dict[str, Any],
        override_method: Optional[NotificationType] = None,
    ) -> bool:
        """Send a notification.

        Args:
            template_name: Name of the template to use
            recipient_name: Name of the recipient
            data: Data to populate the template
            override_method: Override the preferred notification method

        Returns:
            True if notification was sent successfully, False otherwise
        """
        # Get template and recipient
        template = self.templates.get(template_name)
        recipient = self.recipients.get(recipient_name)

        if not template or not recipient:
            print(
                f"Template '{template_name}' or recipient '{recipient_name}' not found"
            )
            return False

        # Determine notification method
        method = override_method or recipient.preferred_method

        # Format template
        try:
            subject = template.subject.format(**data)
            body = template.body.format(**data)
        except KeyError as e:
            print(f"Missing template data: {e}")
            return False

        # Create notification record
        notification = Notification(
            id=f"{template_name}_{recipient_name}_{datetime.now().timestamp()}",
            recipient=recipient,
            template=template,
            data=data,
            scheduled_time=datetime.now(),
        )

        # Send notification
        success = False

        if method == NotificationType.EMAIL and recipient.email:
            success = self.email_service.send_email(
                to_email=recipient.email, subject=subject, body=body
            )
        elif method == NotificationType.SMS and recipient.phone:
            # For SMS, use subject + body or just body
            sms_message = (
                f"{subject}\n\n{body}"
                if len(subject + body) < 160
                else body[:157] + "..."
            )
            success = self.sms_service.send_sms(
                phone_number=recipient.phone, message=sms_message
            )

        # Update notification status
        notification.sent_time = datetime.now()
        notification.status = "sent" if success else "failed"
        if not success:
            notification.error_message = "Failed to send via configured service"

        self.notifications.append(notification)

        # Send webhooks for this event
        if success:
            self._send_webhooks(
                "notification_sent",
                {
                    "template": template_name,
                    "recipient": recipient_name,
                    "method": method.value,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        return success

    def _send_webhooks(self, event: str, data: Dict[str, Any]) -> None:
        """Send webhook notifications for an event.

        Args:
            event: Event name
            data: Event data
        """
        for webhook in self.webhooks:
            if webhook["active"] and event in webhook["events"]:
                payload = {
                    "event": event,
                    "data": data,
                    "webhook_id": webhook.get("id"),
                }

                self.webhook_service.send_webhook(
                    url=webhook["url"], payload=payload, secret=webhook.get("secret")
                )

    def send_due_book_reminders(self, books_due_soon: List[Dict[str, Any]]) -> int:
        """Send reminders for books due soon.

        Args:
            books_due_soon: List of books due soon with member information

        Returns:
            Number of notifications sent successfully
        """
        sent_count = 0

        for book_info in books_due_soon:
            success = self.send_notification(
                template_name="book_due",
                recipient_name=book_info["member_name"],
                data={
                    "title": book_info["title"],
                    "author": book_info["author"],
                    "due_date": book_info["due_date"],
                    "member_name": book_info["member_name"],
                },
            )
            if success:
                sent_count += 1

        return sent_count

    def send_overdue_book_notices(self, overdue_books: List[Dict[str, Any]]) -> int:
        """Send notices for overdue books.

        Args:
            overdue_books: List of overdue books with member information

        Returns:
            Number of notifications sent successfully
        """
        sent_count = 0

        for book_info in overdue_books:
            success = self.send_notification(
                template_name="book_overdue",
                recipient_name=book_info["member_name"],
                data={
                    "title": book_info["title"],
                    "author": book_info["author"],
                    "due_date": book_info["due_date"],
                    "days_overdue": book_info["days_overdue"],
                    "member_name": book_info["member_name"],
                },
            )
            if success:
                sent_count += 1

        return sent_count

    def send_system_alert(
        self, alert_type: str, message: str, severity: str = "normal"
    ) -> bool:
        """Send a system alert to administrators.

        Args:
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity

        Returns:
            True if alert was sent successfully, False otherwise
        """
        # Send to all admin recipients
        admin_recipients = [
            name
            for name, recipient in self.recipients.items()
            if "admin" in name.lower() or "administrator" in name.lower()
        ]

        if not admin_recipients:
            print("No admin recipients found for system alert")
            return False

        sent_count = 0
        for admin_name in admin_recipients:
            success = self.send_notification(
                template_name="system_alert",
                recipient_name=admin_name,
                data={
                    "alert_type": alert_type,
                    "message": message,
                    "severity": severity,
                    "timestamp": datetime.now().isoformat(),
                },
            )
            if success:
                sent_count += 1

        return sent_count > 0

    def get_notification_history(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get notification history.

        Args:
            limit: Maximum number of notifications to return

        Returns:
            List of notification records
        """
        notifications = sorted(
            self.notifications,
            key=lambda x: x.sent_time or x.scheduled_time or datetime.min,
            reverse=True,
        )

        if limit:
            notifications = notifications[:limit]

        return [
            {
                "id": n.id,
                "template": n.template.name,
                "recipient": n.recipient.name,
                "status": n.status,
                "sent_time": n.sent_time.isoformat() if n.sent_time else None,
                "error_message": n.error_message,
            }
            for n in notifications
        ]


class NotificationScheduler:
    """Schedules automatic notifications."""

    def __init__(self, notification_manager: NotificationManager, library=None):
        """Initialize notification scheduler.

        Args:
            notification_manager: NotificationManager instance
            library: Library instance for data access
        """
        self.notification_manager = notification_manager
        self.library = library
        self.enabled = HAS_SCHEDULE

        if self.enabled:
            self._setup_schedules()

    def _setup_schedules(self) -> None:
        """Setup automatic notification schedules."""
        # Daily reminder for books due in 3 days
        schedule.every().day.at("09:00").do(self._send_due_reminders)

        # Daily notice for overdue books
        schedule.every().day.at("10:00").do(self._send_overdue_notices)

        # Weekly system health check
        schedule.every().week.at("08:00").do(self._send_system_health_check)

    def _send_due_reminders(self) -> None:
        """Send reminders for books due soon."""
        if not self.library:
            return

        # Get books due in the next 3 days
        today = date.today()
        due_soon_date = today + timedelta(days=3)

        books_due_soon = []
        for member in self.library.display_members():
            for title, checked_out_book in member.checked_out_books.items():
                try:
                    due_date = datetime.strptime(
                        checked_out_book.due_date, "%Y-%m-%d"
                    ).date()
                    if today <= due_date <= due_soon_date:
                        books_due_soon.append(
                            {
                                "title": checked_out_book.title,
                                "author": checked_out_book.author,
                                "due_date": checked_out_book.due_date,
                                "member_name": member.name,
                            }
                        )
                except ValueError:
                    continue

        if books_due_soon:
            sent_count = self.notification_manager.send_due_book_reminders(
                books_due_soon
            )
            print(f"Sent {sent_count} due book reminders")

    def _send_overdue_notices(self) -> None:
        """Send notices for overdue books."""
        if not self.library:
            return

        overdue_books = self.library.get_overdue_books()

        # Convert to format expected by notification manager
        overdue_list = []
        for member_name, books in overdue_books.items():
            for book_info in books:
                overdue_list.append(
                    {
                        "title": book_info["title"],
                        "author": book_info["author"],
                        "due_date": book_info["due_date"],
                        "days_overdue": book_info["days_overdue"],
                        "member_name": member_name,
                    }
                )

        if overdue_list:
            sent_count = self.notification_manager.send_overdue_book_notices(
                overdue_list
            )
            print(f"Sent {sent_count} overdue book notices")

    def _send_system_health_check(self) -> None:
        """Send weekly system health check."""
        if not self.library:
            return

        stats = self.library.get_library_stats()

        # Check for potential issues
        issues = []

        if stats.get("total_overdue", 0) > 10:
            issues.append(f"High number of overdue books: {stats['total_overdue']}")

        if stats.get("available_books", 0) < stats.get("total_books", 0) * 0.3:
            issues.append("Low availability: Less than 30% of books are available")

        # Send health check notification
        message = "Weekly system health check completed.\n\n"
        message += f"Total books: {stats.get('total_books', 0)}\n"
        message += f"Available books: {stats.get('available_books', 0)}\n"
        message += f"Total members: {stats.get('total_members', 0)}\n"
        message += f"Books issued: {stats.get('issued_books', 0)}\n"

        if issues:
            message += "\nIssues detected:\n" + "\n".join(
                f"- {issue}" for issue in issues
            )
            severity = "high"
        else:
            message += "\nNo issues detected."
            severity = "normal"

        self.notification_manager.send_system_alert(
            alert_type="System Health Check", message=message, severity=severity
        )

    def run_pending(self) -> None:
        """Run any pending scheduled notifications."""
        if self.enabled:
            schedule.run_pending()

    def start_scheduler(self) -> None:
        """Start the notification scheduler (blocking)."""
        if not self.enabled:
            print("Scheduler not available - schedule library not found")
            return

        print("Starting notification scheduler...")
        while True:
            schedule.run_pending()
            import time

            time.sleep(60)  # Check every minute
