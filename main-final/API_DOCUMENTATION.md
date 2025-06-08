# Learning Platform API Documentation

## Base URL
`/api/`

## Authentication
- Uses JWT tokens
- Include token in Authorization header: `Bearer <token>`

## Endpoints

### Root API
- `GET /api/`
  - Lists available API endpoints

### Users
- `POST /api/users/register/`
  - Register new user
  - Required fields: username, email, password
- `GET /api/users/`
  - List all users (admin only)
- `GET /api/users/{id}/`
  - Get user profile
- `PUT /api/users/{id}/profile/`
  - Update user profile
- `POST /api/users/{id}/set_password/`
  - Change password

### Courses
- `GET /api/courses/`
  - List all courses
- `POST /api/courses/`
  - Create new course (instructor only)
- `GET /api/courses/{id}/`
  - Get course details
- `GET /api/courses/{id}/lessons/`
  - List course lessons
- `GET /api/courses/{id}/reviews/`
  - List course reviews
- `POST /api/courses/{id}/reviews/`
  - Add review to course

## Example Requests

### User Registration
```http
POST /api/users/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### Get Course Details
```http
GET /api/courses/1/
Authorization: Bearer your.jwt.token
```

## Response Codes
- 200 OK - Successful request
- 201 Created - Resource created
- 400 Bad Request - Invalid input
- 401 Unauthorized - Authentication required
- 403 Forbidden - Insufficient permissions
- 404 Not Found - Resource not found

## Server Management

### Production Deployment
For persistent Django server operation:

1. **Using Gunicorn + Nginx**:
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn (development)
gunicorn --bind 0.0.0.0:8000 main.wsgi:application

# Production setup with Nginx:
# Configure as systemd service to auto-restart
```

2. **Systemd Service** (for auto-restart):
Create `/etc/systemd/system/gunicorn.service`:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=youruser
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/gunicorn --workers 3 --bind unix:/path/to/your/project/main.sock main.wsgi:application

[Install]
WantedBy=multi-user.target
```

## Android Client Resilience

Implement these best practices in your Android app:

1. **Retry Mechanism**:
```kotlin
private suspend fun <T> withRetry(
    maxRetries: Int = 3,
    initialDelay: Long = 1000, // 1 second
    maxDelay: Long = 10000, // 10 seconds
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelay
    repeat(maxRetries) { attempt ->
        try {
            return block()
        } catch (e: Exception) {
            if (attempt == maxRetries - 1) throw e
            delay(currentDelay)
            currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelay)
        }
    }
    throw IllegalStateException("Should not reach here")
}
```

2. **Connection Timeout**:
```kotlin
val client = OkHttpClient.Builder()
    .connectTimeout(10, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .writeTimeout(30, TimeUnit.SECONDS)
    .build()
```

3. **Health Check Endpoint**:
Android can periodically check `/api/health/` before making requests.
