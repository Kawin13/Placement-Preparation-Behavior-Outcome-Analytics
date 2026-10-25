"""
Unit and integration tests for the Secure Online Judge service:
- Python execution & output matching
- Java execution & compilation
- Timeout protection against infinite loops
- AST security validation against malicious code injection
"""

import pytest
from app.services.judge import (
    execute_python_code,
    execute_java_code,
    execute_test_case,
    evaluate_batch,
    validate_python_security,
    validate_java_security,
    SecurityValidationError,
)


def test_python_security_blocks_malicious_imports():
    malicious_scripts = [
        "import os\nos.system('echo hacked')",
        "import subprocess\nsubprocess.run(['dir'])",
        "import socket\ns = socket.socket()",
        "from shutil import rmtree",
        "open('secret.txt', 'w').write('bad')",
        "eval('2 + 2')",
        "exec('print(1)')",
    ]
    for code in malicious_scripts:
        with pytest.raises(SecurityValidationError):
            validate_python_security(code)


def test_java_security_blocks_dangerous_apis():
    malicious_java = [
        "import java.io.File;\npublic class Main { public static void main(String[] args) {} }",
        "public class Main { public static void main(String[] args) { ProcessBuilder pb = new ProcessBuilder(); } }",
        "public class Main { public static void main(String[] args) { Runtime.getRuntime().exec('calc'); } }",
        "import java.net.URL;\npublic class Main {}",
    ]
    for code in malicious_java:
        with pytest.raises(SecurityValidationError):
            validate_java_security(code)


def test_python_fizzbuzz_accepted():
    code = """import sys

line = sys.stdin.read().strip()
if line:
    n = int(line)
    res = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            res.append("FizzBuzz")
        elif i % 3 == 0:
            res.append("Fizz")
        elif i % 5 == 0:
            res.append("Buzz")
        else:
            res.append(str(i))
    print(" ".join(res))
"""
    result = execute_test_case(
        language="python",
        code=code,
        input_data="5",
        expected_output="1 2 Fizz 4 Buzz",
        time_limit_ms=2000,
    )
    assert result["verdict"] == "ACCEPTED"
    assert result["passed"] is True
    assert result["runtime_ms"] > 0


def test_python_wrong_answer():
    code = "print('incorrect output')"
    result = execute_test_case(
        language="python",
        code=code,
        input_data="5",
        expected_output="1 2 Fizz 4 Buzz",
        time_limit_ms=2000,
    )
    assert result["verdict"] == "WRONG_ANSWER"
    assert result["passed"] is False


def test_python_timeout_protection():
    code = """while True:
    pass
"""
    result = execute_test_case(
        language="python",
        code=code,
        input_data="",
        expected_output="",
        time_limit_ms=1000,
    )
    assert result["verdict"] == "TIME_LIMIT_EXCEEDED"
    assert result["passed"] is False


def test_python_syntax_error():
    code = "def broken_code(:\n    pass"
    result = execute_test_case(
        language="python",
        code=code,
        input_data="",
        expected_output="",
        time_limit_ms=1000,
    )
    assert result["verdict"] == "COMPILATION_ERROR"
    assert result["passed"] is False


def test_java_execution_accepted():
    code = """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            System.out.println(a + b);
        }
    }
}
"""
    result = execute_test_case(
        language="java",
        code=code,
        input_data="12 34",
        expected_output="46",
        time_limit_ms=3000,
    )
    assert result["verdict"] == "ACCEPTED"
    assert result["passed"] is True


def test_batch_evaluation():
    code = """import sys
lines = sys.stdin.read().splitlines()
if lines:
    nums = list(map(int, lines[0].strip().split()))
    target = int(lines[1].strip())
    seen = {}
    for i, n in enumerate(nums):
        comp = target - n
        if comp in seen:
            print(f"{seen[comp]} {i}")
            break
        seen[n] = i
"""
    test_cases = [
        {"input_data": "2 7 11 15\n9", "expected_output": "0 1", "is_hidden": False, "order_index": 1},
        {"input_data": "3 2 4\n6", "expected_output": "1 2", "is_hidden": False, "order_index": 2},
        {"input_data": "3 3\n6", "expected_output": "0 1", "is_hidden": True, "order_index": 3},
    ]
    summary = evaluate_batch("python", code, test_cases)
    assert summary["verdict"] == "ACCEPTED"
    assert summary["test_cases_passed"] == 3
    assert summary["total_test_cases"] == 3
    assert len(summary["results"]) == 3
    assert summary["results"][2]["input"] == "[Hidden Test Case]"
    assert summary["results"][2]["actual_output"] == "[Hidden Output]"


def test_judge_feature_toggle_disabled(monkeypatch):
    """When CODE_EXECUTION_ENABLED is False, judge must reject code with verdict DISABLED."""
    from app.core.config import settings
    monkeypatch.setattr(settings, "CODE_EXECUTION_ENABLED", False)

    result = execute_test_case(
        language="python",
        code="print('Hello World')",
        input_data="",
        expected_output="Hello World",
        time_limit_ms=1000,
    )
    assert result["verdict"] == "DISABLED"
    assert "disabled" in result["error"].lower()


def test_judge_code_size_limit_exceeded(monkeypatch):
    """Submissions exceeding maximum byte size must be safely rejected."""
    from app.core.config import settings
    monkeypatch.setattr(settings, "CODE_EXECUTION_MAX_CODE_BYTES", 100)

    large_code = "# " + ("x" * 200) + "\nprint('oversized')"
    result = execute_test_case(
        language="python",
        code=large_code,
        input_data="",
        expected_output="",
        time_limit_ms=1000,
    )
    assert result["verdict"] == "COMPILATION_ERROR"
    assert "exceeds" in result["error"].lower()


def test_judge_subprocess_env_sanitization():
    """Verify clean_env never contains server secrets such as DATABASE_URL, SECRET_KEY, GEMINI_API_KEY."""
    from app.services.judge import _get_clean_subprocess_env
    clean = _get_clean_subprocess_env("C:\\temp\\dummy")
    assert "DATABASE_URL" not in clean
    assert "SECRET_KEY" not in clean
    assert "GEMINI_API_KEY" not in clean
    assert "TEMP" in clean
    assert "TMP" in clean
    assert "PYTHONIOENCODING" in clean

