### Django application for tree-structure menus
<br/>

Runs on *Python 3.12.2*

Uses *Django 5.2*, *SQLite 3.41.2*

All requirements are listed in [requirements.txt](/app/requirements.txt)

DB is prepopulated with test data

Task description for the API: [task_description.docx](/task_description.docx)

<br/><br/>

**To use locally run following steps:**

**Download project and cd into it**

**Activate venv:**
1. `python -m venv venv`
2. `.\venv\Scripts\activate` (for Windows)
`source ./venv/bin/activate` (for Linux)
3. `pip install -r requirements.txt`

**Start application:** `python manage.py runserver`

**Open menus in browser:** `http://127.0.0.1:8000/`

**Admin panel to manage application**: `http://127.0.0.1:8000/admin/` (login: admin password: admin):

**Shutdown:** `Ctrl+C`