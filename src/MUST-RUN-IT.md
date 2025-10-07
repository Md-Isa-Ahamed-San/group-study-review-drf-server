### **Important Note: Creating & Using the Virtual Environment**

When you are trying to **run the project for the first time**, you must create a Python virtual environment to keep your dependencies isolated from the global Python.

```powershell
python -m venv ./venv-drf
```

**Why this is important:**

- Keeps your project’s dependencies **separate** from global Python, avoiding conflicts.
- Ensures your project works consistently on other machines or deployment environments.
- Allows you to upgrade or change packages **without breaking global Python** or other projects.

---

### **Step 1: Select Interpreter in VS Code**

After creating `venv-drf`, you need to **tell VS Code to use it as your project interpreter**:

1. Open VS Code → **Command Palette** → `Python: Select Interpreter`
2. Choose **“Enter interpreter path” → Find…”**
3. Navigate to your project folder → `venv-drf\Scripts\python.exe` (Windows) or `venv-drf/bin/python` (Linux/macOS)
4. VS Code now uses this virtual environment automatically for terminals, running scripts, and linting.

---

### **Step 2: Activate the venv before running commands**

```powershell
.\venv-drf\Scripts\activate
```

Then run commands like:

```powershell
django-admin startproject myproject .   # this is to create a project

python manage.py runserver
```

- Any `pip install` now goes **inside `venv-drf`**, keeping the environment clean.
- VS Code automatically uses this environment as long as the interpreter is selected.

---

This ensures your project is **fully isolated, reproducible, and safe** to work on, even if the global Python or pip is broken.
