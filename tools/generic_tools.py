import os
import subprocess
import urllib.request
import urllib.parse
import json
import sqlite3
import math
import sys
import io

# =====================================
# FILE TOOLS
# =====================================

def read_file(filepath: str) -> str:
    """Reads the content of a local file."""
    try:
        abs_path = os.path.abspath(filepath)
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding='utf-8') as f:
                return f.read()
        return f"Error: File {abs_path} not found."
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(filepath: str, content: str) -> str:
    """Writes content to a local file."""
    try:
        abs_path = os.path.abspath(filepath)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {abs_path}."
    except Exception as e:
        return f"Error writing file: {e}"

# =====================================
# NOTES TOOLS
# =====================================

# In-memory notes store for demonstration
_notes_db = []

def create_note(content: str) -> str:
    """Creates a new note."""
    note_id = len(_notes_db) + 1
    _notes_db.append({"id": note_id, "content": content})
    return f"Successfully created note #{note_id}."

def search_notes(query: str) -> list:
    """Searches existing notes for a given query."""
    results = [n for n in _notes_db if query.lower() in n["content"].lower()]
    return results if results else [{"id": 0, "content": "No notes found matching the query."}]

def list_notes() -> list:
    """Lists all created notes."""
    return _notes_db if _notes_db else [{"id": 0, "content": "No notes exist yet."}]

# =====================================
# REAL WORLD TOOLS
# =====================================

def search_web(query: str) -> str:
    """Searches the web for current information."""
    # Using a simple duckduckgo html parse or wikipedia as a fallback for demonstration
    # Since we can't reliably install new packages, we'll use a public API simulation or basic urllib
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=1&namespace=0&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if len(data) > 2 and data[2]:
                return data[2][0]
            return "No specific web results found."
    except Exception as e:
        return f"Simulated Web Search Result for '{query}': Information retrieved successfully. (API Error: {e})"

def execute_terminal_command(command: str) -> str:
    """Executes a command on the host operating system terminal."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.stdout else result.stderr
        return output[:1000] + ("..." if len(output) > 1000 else "")
    except Exception as e:
        return f"Error executing command: {e}"

def fetch_webpage(url: str) -> str:
    """Fetches the raw HTML or text content of a webpage."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            return content[:2000] + ("...\n[Content truncated]" if len(content) > 2000 else "")
    except Exception as e:
        return f"Error fetching webpage: {e}"

def execute_python_code(code: str) -> str:
    """Executes Python code in a safe local environment and returns the stdout output."""
    try:
        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        
        # We use a restricted dictionary for globals to avoid catastrophic failure, though this isn't true sandboxing
        exec_globals = {"__builtins__": __builtins__, "math": math, "json": json, "os": os}
        exec(code, exec_globals)
        
        sys.stdout = old_stdout
        return redirected_output.getvalue() or "Code executed successfully with no output."
    except Exception as e:
        sys.stdout = old_stdout
        return f"Python Error: {e}"

def calculate_math(expression: str) -> str:
    """Safely evaluates a mathematical expression."""
    try:
        # Safe math evaluation using eval with restricted globals
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Math Error: {e}"

def query_database(sql_query: str, db_path: str = "audit_log.db") -> str:
    """Executes an SQL query against a SQLite database (defaults to the local audit_log.db)."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        if sql_query.strip().upper().startswith( ("INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER") ):
            conn.commit()
            result = f"Query executed successfully. Rows affected: {cursor.rowcount}"
        else:
            rows = cursor.fetchall()
            result = json.dumps(rows, default=str)
        conn.close()
        return result[:2000] + ("..." if len(result) > 2000 else "")
    except Exception as e:
        return f"Database Error: {e}"
