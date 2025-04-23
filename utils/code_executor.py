# utils/code_executor.py
import io
import contextlib

def execute_code(code):
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {})
    except Exception as e:
        return f"Erreur : {str(e)}"
    return output.getvalue()
