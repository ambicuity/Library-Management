# Enhanced Library Management System - Quick Start Guide

## 🚀 **Get Started in 3 Steps**

### 1. **Clone and Install**
```bash
git clone https://github.com/ambicuity/Library-Management.git
cd Library-Management

# Install enhanced dependencies
pip install -r requirements.txt
```

### 2. **Choose Your Interface**
```bash
# CLI Mode (Traditional + Enhanced Features)
python library_management.py

# REST API Server
python library_management.py --mode api

# Web Interface  
python library_management.py --mode web

# Combined (API + Web)
python library_management.py --mode combined
```

### 3. **Login and Explore**
- **Default Admin**: username: `admin`, password: `admin123`
- **API Docs**: http://localhost:8000/docs (API mode)
- **Web Interface**: http://localhost:8000 (Web mode)

## ✨ **New Enhanced Features**

### 🔒 **Security**
- Role-based access control (Admin/Librarian/Member)
- Data encryption and secure backups
- Audit logging and transaction tracking

### 🌐 **Integration**
- REST API with 40+ endpoints
- Export data to CSV, JSON, PDF
- Webhook notifications for real-time updates

### 💻 **User Experience**
- Search autocomplete and fuzzy matching
- Dark mode and accessibility support
- Multi-language interface (English/Spanish)

### 🔔 **Notifications**
- Email/SMS reminders for due books
- System alerts and health monitoring
- Customizable notification templates

### 🧩 **Developer Tools**
- CI/CD pipeline with GitHub Actions
- Docker containerization
- Comprehensive monitoring and logging

## 🐳 **Docker Quick Start**

```bash
# Build and run
docker build -t library-management .
docker run -p 8000:8000 library-management

# Or use docker-compose (if available)
docker-compose up
```

## 📱 **API Quick Examples**

```bash
# Get all books
curl http://localhost:8000/books

# Search books
curl -X POST http://localhost:8000/books/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Python", "search_type": "title"}'

# Export books to PDF
curl http://localhost:8000/export/books?format=pdf -o books.pdf
```

## 🎯 **Quick Demo**

Run the feature demonstration:
```bash
python demo_enhanced_features.py
```

This will showcase all enhanced features including authentication, search, notifications, and monitoring.

## 📚 **Next Steps**

1. **Customize**: Modify themes, add translations, configure notifications
2. **Integrate**: Use the REST API to connect with external systems
3. **Scale**: Deploy with Docker, set up CI/CD, enable monitoring
4. **Secure**: Change default passwords, configure encryption, set up backups

## 🆘 **Need Help?**

- **Documentation**: See `ENHANCED_FEATURES.md` for complete details
- **API Reference**: Visit `/docs` endpoint when running API mode
- **Issues**: Check the repository issues for common problems
- **Support**: Contact the development team

---

**🎉 Enjoy your enhanced library management experience!**