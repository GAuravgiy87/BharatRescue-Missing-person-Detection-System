"# BharatRescue-Missing-person-Detection-System" 
Overview
This is a Missing Person Detection System built with Flask that uses facial recognition technology to help locate missing persons. The application allows users to report missing persons, upload photos for facial recognition matching, and sends automated email alerts when potential matches are detected. It includes both public reporting features and an admin dashboard for case management.

User Preferences
Preferred communication style: Simple, everyday language.

System Architecture
Backend Framework
Flask: Chosen as the web framework for its simplicity and flexibility in building web applications
SQLAlchemy: Used as the ORM for database operations with support for multiple database backends
Werkzeug: Provides security utilities including password hashing and file handling
Database Design
SQLite/PostgreSQL: Configurable database backend using environment variables, defaulting to SQLite for development
Three main entities:
MissingPerson: Stores personal details, contact information, photos, and facial encodings
Detection: Tracks when facial recognition finds potential matches
Admin: Manages administrative access to the system
Face encoding storage: Binary data stored directly in the database for efficient facial recognition comparisons
Facial Recognition System
face_recognition library: Implements facial detection and encoding extraction from uploaded photos
OpenCV integration: Handles image processing and computer vision operations
Encoding comparison: Uses tolerance-based matching to identify potential matches between stored and uploaded photos
Email Notification System
Flask-Mail: Handles automated email alerts when missing persons are detected
SMTP configuration: Supports various email providers through environment variables
Alert templates: Structured email notifications sent to contacts when matches are found
File Management
Secure file uploads: Validates file types and sizes with configurable limits
Photo storage: Organized file system for storing uploaded photos
Image processing: Handles multiple image formats (PNG, JPG, JPEG, GIF)
Security Features
Password hashing: Uses Werkzeug's security utilities for admin authentication
File validation: Restricts upload types and sizes to prevent security issues
Session management: Secure session handling with configurable secret keys
Frontend Architecture
Bootstrap 5: Dark theme UI framework for responsive design
Jinja2 templating: Server-side rendering with template inheritance
Font Awesome: Icon library for enhanced user interface
JavaScript enhancements: Form validation, image previews, and user interaction improvements
External Dependencies
Core Web Framework
Flask: Web application framework
Flask-SQLAlchemy: Database ORM integration
Flask-Mail: Email sending capabilities
Computer Vision and AI
face_recognition: Primary facial recognition library
OpenCV (cv2): Computer vision and image processing
PIL (Pillow): Image manipulation and processing
NumPy: Numerical operations for image data
Frontend Libraries
Bootstrap 5: CSS framework with dark theme
Font Awesome: Icon library
jQuery: JavaScript utilities (implied by Bootstrap usage)
Database Support
SQLAlchemy: Database abstraction layer supporting multiple backends
Database drivers: SQLite (built-in), PostgreSQL support through environment configuration
Email Services
SMTP servers: Configurable email providers (default: Gmail SMTP)
Flask-Mail: Email template rendering and sending
File Processing
Werkzeug: File upload security and handling
Secure filename utilities: Sanitizes uploaded file names
Environment Configuration
OS environment variables: Database URLs, email credentials, and security keys
Development defaults: Fallback configurations for local development
