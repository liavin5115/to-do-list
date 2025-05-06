# Todo List Application

A collaborative task management application built with Flask, featuring a Trello-like interface with boards, lists, and cards.

## Features

- **User Authentication**
  - Register/Login functionality
  - Profile management
  - Secure password handling

- **Board Management**
  - Create, edit, and delete boards
  - Share boards with other users
  - Different permission levels (View, Edit, Manage)
  - Drag and drop board reordering

- **List Management**
  - Create multiple lists within boards
  - Rename and delete lists
  - Drag and drop list reordering

- **Card Management**
  - Create cards with titles and descriptions
  - Set deadlines for cards
  - Mark cards as complete
  - Add comments to cards
  - Drag and drop card reordering
  - Move cards between lists

- **UI/UX**
  - Responsive design
  - Dark/Light theme toggle
  - Real-time updates
  - Intuitive drag-and-drop interface

## Technology Stack

- **Backend**
  - Python 3.x
  - Flask
  - SQLAlchemy
  - Flask-Login
  - Flask-Migrate

- **Frontend**
  - HTML/CSS
  - JavaScript
  - Bootstrap 5
  - Font Awesome
  - SortableJS

- **Database**
  - SQLite

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd todo-list
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
todo-list/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── main.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   └── themes.css
│   │   └── js/
│   │       ├── board.js
│   │       ├── sortable.js
│   │       └── theme.js
│   └── templates/
│       ├── auth/
│       │   ├── login.html
│       │   ├── profile.html
│       │   └── register.html
│       ├── base.html
│       ├── board.html
│       └── index.html
├── instance/
├── migrations/
├── config.py
├── requirements.txt
├── README.md
└── run.py
```

## Environment Variables

No environment variables are required for basic setup as the application uses default configurations. For production, consider setting:

- `SECRET_KEY`: A secure secret key
- `DATABASE_URL`: Your database connection string

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask documentation
- Bootstrap documentation
- SortableJS library