# Copilot Instructions for TwINSA

## Project Overview
TwINSA is a Python-based user management system with registration, login, and user data storage. The codebase is organized for educational purposes and demonstrates basic authentication, user data handling, and password validation.

## Key Components
- `registration.py`: Handles user registration, password strength validation, and basic email checks. Interacts with the user database.
- `users_db.py`: Implements a simple JSON-based user database with add, remove, and authentication methods. Example: `UsersDatabase.add_user(username, password)`.
- `user.py`: Defines the `user` class with profile, followers, and social features.
- `registration_test.py`: Contains tests for registration logic. Import and call registration functions directly for testing.
- `Login_Logout.ipynb`: Contains login logic (using SQLite, not JSON) and web route examples. Not fully integrated with the rest of the codebase.

## Patterns & Conventions
- User data is stored in a JSON file (`users_database.json`) via `UsersDatabase`.
- Passwords are stored in plaintext (for demo only; not secure for production).
- Registration requires strong passwords (min 8 chars, upper/lower/digit/special).
- Minimal email format validation: must contain `@` and `.`.
- The `user` class is not directly linked to the database logic; it is used for in-memory user representation.
- Tests are run by executing `registration_test.py`.

## Developer Workflows
- **Add new user fields:** Update both `user.py` and `users_db.py` to keep data in sync.
- **Run tests:** Execute `registration_test.py` directly.
- **Debug registration:** Print statements are used for feedback; errors are not raised but printed.
- **Database reset:** Delete `users_database.json` to clear all users.

## Integration Notes
- `Login_Logout.ipynb` uses SQLite and Flask-style routes, which are not integrated with the JSON-based backend. Treat as a separate example.
- No external dependencies except Python standard library (json, os).

## Example Usage
```python
from registration import registration
registration()
```

## Limitations
- No password hashing or secure storage.
- No real email validation or sending.
- No web interface (except in notebook example).

---
For major changes, update this file to keep AI agents productive.
