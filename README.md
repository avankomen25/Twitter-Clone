# Twitter Clone

A simple Twitter-like web app built with FastAPI, Jinja2, and SQLite.

## Screenshot Example

![Main Page](labsubmission.png)

## Features

- View all messages on the home page, sorted newest first
- Each message displays the text, timestamp, username, and age of the poster
- Styled with custom CSS served from static files


## Setup

**1. Install dependencies:**

```bash
pip install fastapi uvicorn jinja2
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

- `/`
- `/login`
- `/logout`
- `/create_message`
- `/create_user`

## Dependencies

- Python
- FastAPI
- Uvicorn
- Jinja2
- SQLite3 (built into Python)