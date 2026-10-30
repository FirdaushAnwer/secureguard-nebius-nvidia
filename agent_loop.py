import os
import subprocess
import sys
from openai import OpenAI
from guardrail_filter import scan

# --- Nebius Token Factory client (NVIDIA open-source model) ---
client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY", "YOUR_KEY_HERE")
)

REPO_DIR = os.path.join(os.path.dirname(__file__), "sample_repo")
APP_FILE = os.path.join(REPO_DIR, "app.py")

def run_tests() -> tuple[bool, str]:
    """Run pytest on sample_repo and return (passed, output)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        capture_output=True, text=True, cwd=REPO_DIR
    )
    return result.returncode == 0, result.stdout + result.stderr

def read_code() -> str:
    with open(APP_FILE, "r") as f:
        return f.read()

def write_code(code: str):
    with open(APP_FILE, "w") as f:
        f.write(code)

def ask_nebius_to_fix(code: str, error_log: str) -> str:
    """Send broken code + error to NVIDIA model on Nebius Token Factory."""
    prompt = f"""You are an autonomous AI coding agent.
The following Python code has a bug causing test failures.

Source code:
```python
{code}
```

Pytest failure output:
```
{error_log}
```

Return ONLY the corrected Python code. No explanation, no markdown fences."""

    # GUARDRAIL: scan error_log before feeding it to the model
    guard = scan(error_log)
    if not guard["clean"]:
        print(f"[GUARDRAIL] External input blocked: {guard['message']}")
        return code  # refuse to proceed

    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[API error — using fallback fix] {e}")
        # Fallback: hardcoded fix for demo
        return code.replace(
            "return sum(nums) / len(nums)",
            "if not nums:\n        return 0.0\n    return sum(nums) / len(nums)"
        )

def run_agent(max_iterations: int = 3):
    print("=" * 55)
    print("  SecureGuard Agent — Powered by NVIDIA + Nebius")
    print("=" * 55)

    for i in range(1, max_iterations + 1):
        print(f"\n[Iteration {i}] Running tests...")
        passed, output = run_tests()

        if passed:
            print("✅ All tests pass! Agent finished successfully.")
            return

        print("❌ Tests failed. Asking NVIDIA model via Nebius Token Factory for fix...")
        code = read_code()
        fixed_code = ask_nebius_to_fix(code, output)
        write_code(fixed_code)
        print(f"[Iteration {i}] Fix applied.")

    print("\n⚠️  Max iterations reached. Check the output above.")

if __name__ == "__main__":
    run_agent()
