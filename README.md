# The Social Network
 
A Twitter-like web app built with FastAPI, Jinja2, and SQLite.
 
## Screenshot
 
![Main Page](screenshot.png)
 
## Features
 
- View all messages sorted newest first with pagination (50 per page)
- Each message displays the username, age, timestamp, and message body
- Robohash avatars auto-generated per username
- URLs in messages automatically converted to clickable links
- User authentication with login/logout via cookies
- Create, delete messages
- Search messages using SQL LIKE
- JSON endpoint for all messages
- Auto-login on account creation
- Delete account
- Change password
- CMC-themed CSS with light grey background and cardinal/gold colors
- 200+ user accounts with 40,000+ randomly generated messages
- SQL and HTML injection protected
- Language support for English, Spanish, and Tagalog
## Setup
 
**1. Install dependencies:**
```bash
pip install fastapi uvicorn jinja2 faker
```
 
**2. Create the database:**
```bash
python db_create.py
```
 
**3. Run the app:**
```bash
python main.py
```
 
**4. Open in browser:**
```
http://127.0.0.1:8080
```
 
## Routes
 
- `/` -- Home page, all messages paginated
- `/login` -- Login with username and password
- `/logout` -- Clears login cookies
- `/create_user` -- Create a new user account
- `/create_message` -- Post a new message
- `/delete_message/{id}` -- Delete a message
- `/delete_account` -- Delete your account
- `/change_password` -- Change your password
- `/search` -- Search messages with SQL LIKE
- `/json` -- JSON endpoint for all messages
## Dependencies
 
- Python 3.x
- FastAPI
- Uvicorn
- Jinja2
- SQLite3 (built into Python)
- Faker