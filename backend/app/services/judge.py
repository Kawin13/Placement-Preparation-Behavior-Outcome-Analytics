"""
Secure Online Judge Service:
Executes student code (Python and Java) against test cases in an isolated subprocess sandbox.
Features:
- Static AST/source code security checks to reject malicious libraries and primitives
- Enforced execution timeouts (prevent infinite loops)
- Standardized output diffing (handling trailing spaces and CRLF differences)
- Clean temporary directory execution with automatic cleanup
- Support for run-code (sample cases + custom input) and submit-solution (sample + hidden cases)
"""

import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional

# Banned modules and builtins for Python submissions
PYTHON_BANNED_MODULES = {
    "os",
    "subprocess",
    "socket",
    "shutil",
    "ctypes",
    "urllib",
    "requests",
    "http",
    "pty",
    "posix",
    "resource",
    "signal",
    "inspect",
    "importlib",
    "multiprocessing",
    "threading",
    "asyncio",
    "pickle",
    "webbrowser",
    "ftplib",
    "poplib",
    "imaplib",
    "smtplib",
}

PYTHON_BANNED_BUILTINS = {
    "eval",
    "exec",
    "open",
    "compile",
    "__import__",
    "breakpoint",
}

# Dangerous patterns for Java submissions
JAVA_BANNED_PATTERNS = [
    r"java\.io\.File\b",
    r"\bFile\b",
    r"\bFileInputStream\b",
    r"\bFileOutputStream\b",
    r"\bRandomAccessFile\b",
    r"\bProcess\b",
    r"\bProcessBuilder\b",
    r"\bRuntime\b",
    r"java\.lang\.reflect",
    r"java\.net",
    r"java\.nio",
    r"javax\.script",
    r"System\.exit",
]


class SecurityValidationError(Exception):
    """Raised when submitted code contains prohibited calls or security hazards."""
    pass


def validate_python_security(code: str) -> None:
    """Performs static AST validation on Python code to block dangerous operations."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise SyntaxError(f"Syntax error at line {e.lineno}: {e.msg}") from e

    for node in ast.walk(tree):
        # Block banned module imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0]
                if root_module in PYTHON_BANNED_MODULES:
                    raise SecurityValidationError(f"Prohibited module import: '{root_module}'")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_module = node.module.split(".")[0]
                if root_module in PYTHON_BANNED_MODULES:
                    raise SecurityValidationError(f"Prohibited module import: '{root_module}'")

        # Block banned builtin calls (eval, exec, open, etc.)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in PYTHON_BANNED_BUILTINS:
                    raise SecurityValidationError(f"Prohibited function call: '{node.func.id}()'")


def validate_java_security(code: str) -> None:
    """Performs regex validation on Java source to block file/process/network manipulation."""
    for pattern in JAVA_BANNED_PATTERNS:
        if re.search(pattern, code):
            clean_name = pattern.replace(r"\.", ".").replace(r"\\", "")
            raise SecurityValidationError(f"Prohibited Java API detected: '{clean_name}'")


def normalize_output(text: str) -> str:
    """Normalizes output lines by trimming trailing spaces and standardizing line breaks."""
    if text is None:
        return ""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    # Strip whitespace from right side of each line
    cleaned = [line.rstrip() for line in lines]
    # Strip empty trailing lines from the end
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned)


def execute_python_code(
    code: str,
    input_data: str,
    time_limit_sec: float = 3.0,
    max_output_bytes: int = 65536,
) -> Dict[str, Any]:
    """Executes Python code in an isolated directory with stdin piping and timeout limits."""
    # 1. Security Check
    try:
        validate_python_security(code)
    except (SyntaxError, SecurityValidationError) as e:
        return {
            "verdict": "COMPILATION_ERROR",
            "runtime_ms": 0,
            "stdout": "",
            "error": str(e),
        }

    work_dir = tempfile.mkdtemp(prefix="judge_py_")
    script_path = os.path.join(work_dir, "solution.py")
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        python_bin = sys.executable

        start_time = time.perf_counter()
        proc = subprocess.Popen(
            [python_bin, "solution.py"],
            cwd=work_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        try:
            stdout, stderr = proc.communicate(input=input_data, timeout=time_limit_sec)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            # Cap stdout size
            if len(stdout) > max_output_bytes:
                stdout = stdout[:max_output_bytes] + "\n[Output truncated: exceeded 64KB]"

            if proc.returncode != 0:
                return {
                    "verdict": "RUNTIME_ERROR",
                    "runtime_ms": elapsed_ms,
                    "stdout": stdout,
                    "error": stderr.strip() if stderr else f"Process exited with code {proc.returncode}",
                }

            return {
                "verdict": "OK",
                "runtime_ms": max(1, elapsed_ms),
                "stdout": stdout,
                "error": None,
            }

        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                proc.communicate(timeout=0.5)
            except Exception:
                pass
            return {
                "verdict": "TIME_LIMIT_EXCEEDED",
                "runtime_ms": int(time_limit_sec * 1000),
                "stdout": "",
                "error": f"Time limit exceeded ({time_limit_sec:.1f}s)",
            }

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def execute_java_code(
    code: str,
    input_data: str,
    time_limit_sec: float = 3.0,
    compile_limit_sec: float = 5.0,
    max_output_bytes: int = 65536,
) -> Dict[str, Any]:
    """Compiles and executes Java code in a temp directory with strict resource limits."""
    # 1. Security Check
    try:
        validate_java_security(code)
    except SecurityValidationError as e:
        return {
            "verdict": "COMPILATION_ERROR",
            "runtime_ms": 0,
            "stdout": "",
            "error": str(e),
        }

    work_dir = tempfile.mkdtemp(prefix="judge_java_")
    source_path = os.path.join(work_dir, "Main.java")
    try:
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(code)

        # 2. Compile with javac
        compile_start = time.perf_counter()
        compile_proc = subprocess.run(
            ["javac", "-encoding", "UTF-8", "Main.java"],
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=compile_limit_sec,
        )

        if compile_proc.returncode != 0:
            return {
                "verdict": "COMPILATION_ERROR",
                "runtime_ms": 0,
                "stdout": "",
                "error": compile_proc.stderr.strip() if compile_proc.stderr else "Compilation failed",
            }

        # 3. Execute with java
        start_time = time.perf_counter()
        run_proc = subprocess.Popen(
            ["java", "-Xmx256m", "-cp", ".", "Main"],
            cwd=work_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        try:
            stdout, stderr = run_proc.communicate(input=input_data, timeout=time_limit_sec)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            if len(stdout) > max_output_bytes:
                stdout = stdout[:max_output_bytes] + "\n[Output truncated: exceeded 64KB]"

            if run_proc.returncode != 0:
                return {
                    "verdict": "RUNTIME_ERROR",
                    "runtime_ms": elapsed_ms,
                    "stdout": stdout,
                    "error": stderr.strip() if stderr else f"Process exited with code {run_proc.returncode}",
                }

            return {
                "verdict": "OK",
                "runtime_ms": max(1, elapsed_ms),
                "stdout": stdout,
                "error": None,
            }

        except subprocess.TimeoutExpired:
            run_proc.kill()
            try:
                run_proc.communicate(timeout=0.5)
            except Exception:
                pass
            return {
                "verdict": "TIME_LIMIT_EXCEEDED",
                "runtime_ms": int(time_limit_sec * 1000),
                "stdout": "",
                "error": f"Time limit exceeded ({time_limit_sec:.1f}s)",
            }

    except subprocess.TimeoutExpired:
        return {
            "verdict": "COMPILATION_ERROR",
            "runtime_ms": 0,
            "stdout": "",
            "error": "Java compilation timed out",
        }
    except FileNotFoundError as e:
        return {
            "verdict": "COMPILATION_ERROR",
            "runtime_ms": 0,
            "stdout": "",
            "error": f"Java runtime/compiler not found on host: {e}",
        }
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def execute_test_case(
    language: str,
    code: str,
    input_data: str,
    expected_output: Optional[str] = None,
    time_limit_ms: int = 2000,
) -> Dict[str, Any]:
    """Runs a single test case for a given language, comparing against expected output if provided."""
    time_limit_sec = max(1.0, time_limit_ms / 1000.0)
    lang_norm = language.lower().strip()

    if lang_norm == "python":
        exec_res = execute_python_code(code, input_data, time_limit_sec=time_limit_sec)
    elif lang_norm == "java":
        exec_res = execute_java_code(code, input_data, time_limit_sec=time_limit_sec)
    else:
        return {
            "verdict": "COMPILATION_ERROR",
            "runtime_ms": 0,
            "stdout": "",
            "error": f"Unsupported language: '{language}'. Supported: 'python', 'java'.",
            "passed": False,
        }

    verdict = exec_res["verdict"]
    actual_stdout = exec_res["stdout"]
    norm_actual = normalize_output(actual_stdout)

    # Check output match if no runtime/compile/timeout error
    passed = False
    if verdict == "OK":
        if expected_output is not None:
            norm_expected = normalize_output(expected_output)
            if norm_actual == norm_expected:
                verdict = "ACCEPTED"
                passed = True
            else:
                verdict = "WRONG_ANSWER"
                passed = False
        else:
            verdict = "ACCEPTED"
            passed = True

    return {
        "verdict": verdict,
        "runtime_ms": exec_res["runtime_ms"],
        "stdout": actual_stdout,
        "normalized_stdout": norm_actual,
        "error": exec_res["error"],
        "passed": passed,
    }


def evaluate_batch(
    language: str,
    code: str,
    test_cases: List[Dict[str, Any]],
    stop_on_first_failure: bool = False,
) -> Dict[str, Any]:
    """
    Evaluates submitted code across a list of test cases.
    Returns aggregated verdict, runtime statistics, and per-case results.
    """
    total = len(test_cases)
    passed_count = 0
    max_runtime_ms = 0
    final_verdict = "ACCEPTED"
    failed_index: Optional[int] = None
    first_error: Optional[str] = None
    sample_stdout: Optional[str] = None

    results: List[Dict[str, Any]] = []

    for idx, tc in enumerate(test_cases, start=1):
        input_data = tc.get("input_data", "")
        expected_output = tc.get("expected_output", "")
        time_limit_ms = tc.get("time_limit_ms", 2000)
        is_hidden = tc.get("is_hidden", False)

        res = execute_test_case(
            language=language,
            code=code,
            input_data=input_data,
            expected_output=expected_output,
            time_limit_ms=time_limit_ms,
        )

        max_runtime_ms = max(max_runtime_ms, res["runtime_ms"])

        case_summary = {
            "test_case_number": idx,
            "order_index": tc.get("order_index", idx),
            "is_hidden": is_hidden,
            "verdict": res["verdict"],
            "runtime_ms": res["runtime_ms"],
            "passed": res["passed"],
        }

        # For public test cases, provide full input/output details
        if not is_hidden:
            case_summary["input"] = input_data
            case_summary["expected_output"] = expected_output
            case_summary["actual_output"] = res["stdout"]
            case_summary["error"] = res["error"]
        else:
            # Mask hidden test case data to avoid leaking test secrets
            case_summary["input"] = "[Hidden Test Case]"
            case_summary["expected_output"] = "[Hidden Test Case]"
            case_summary["actual_output"] = "[Hidden Output]"
            case_summary["error"] = res["error"] if res["verdict"] in ("COMPILATION_ERROR", "RUNTIME_ERROR", "TIME_LIMIT_EXCEEDED") else None

        results.append(case_summary)

        if res["passed"]:
            passed_count += 1
        else:
            if final_verdict == "ACCEPTED":
                final_verdict = res["verdict"]
                failed_index = idx
                first_error = res["error"]
                sample_stdout = res["stdout"]

            if stop_on_first_failure:
                break

    return {
        "verdict": final_verdict,
        "test_cases_passed": passed_count,
        "total_test_cases": total,
        "failed_test_case_index": failed_index,
        "runtime_ms": max_runtime_ms,
        "error_message": first_error,
        "stdout_sample": sample_stdout,
        "results": results,
    }
