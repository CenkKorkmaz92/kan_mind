# KanMind Django Backend

A robust Django REST Framework backend for a Kanban board application. This backend provides user authentication, board/task/comment management, and strict permission enforcement. **Frontend code is not included or tracked here.**

---

## Features
- User registration and login with token authentication
- Board, task, and comment CRUD operations
- Board membership and task assignment
- Strict permissions (only board members/owners can modify, only comment authors can delete, etc.)
- High local test coverage (95%+)
- CORS enabled for frontend integration

---

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- (Recommended) Virtual environment tool: `venv` or `virtualenv`

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/CenkKorkmaz92/kan_mind.git
cd kan_mind
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations
```bash
python manage.py migrate
```

### 5. Create a Superuser (Admin Account)
```bash
python manage.py createsuperuser
```
Follow the prompts to set username, email, and password.

### 6. Run the Development Server
```bash
python manage.py runserver
```
The backend will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## API Usage
- All API endpoints are prefixed with `/api/` (e.g., `/api/login/`, `/api/boards/`).
- Use a tool like Postman or your frontend to interact with the API.
- Authentication is via token (obtainable via `/api/login/`).

### Common Endpoints
- `POST /api/registration/` — Register a new user
- `POST /api/login/` — Log in and receive an authentication token
- `GET /api/boards/` — List boards for the authenticated user
- `POST /api/boards/` — Create a new board
- `GET /api/boards/<board_id>/` — Get board details and tasks
- `POST /api/tasks/` — Create a new task (must be a board member)
- `GET /api/email-check/?email=...` — Check if an email exists

---

## Running Tests & Coverage
- Automated tests cover all endpoints, permissions, and edge cases.
- **Test files are not tracked in the repository** (see `.gitignore`). They are for local development only.
- To run tests and check coverage locally:
```bash
coverage run manage.py test
coverage report -m
```

---

## Error Logging
- All backend errors are logged to `backend_errors.log` in the backend root directory.
- This file is ignored by git (see `.gitignore`).

---

## Notes
- Add users to boards as members to allow task creation and assignment.
- For production, set `DEBUG = False` and configure `ALLOWED_HOSTS` in `core/settings.py`.
- See code docstrings for detailed API and logic documentation.

---

## License
This project is for educational/demo purposes. See LICENSE if present.
