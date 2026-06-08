from app.ai_engine import ask_ai


def explain_code(code: str) -> str:
    prompt = f"""
You are an expert programming tutor.

Explain the following code for a beginner.

Code:
{code[:12000]}

Provide:

1. Overview
   - What the program does

2. Step-by-Step Explanation
   - Explain each important section

3. Key Concepts
   - Mention important programming concepts used

4. Beginner Notes
   - Explain anything a beginner might find confusing

Keep explanations clear and educational.
"""
    return ask_ai(prompt)


def find_bugs(code: str) -> str:
    prompt = f"""
You are a senior software engineer performing a code review.

Code:
{code[:12000]}

Analyze the code and provide:

1. Potential Bugs
2. Logic Errors
3. Runtime Risks
4. Edge Cases
5. Security Issues (if any)
6. Suggested Fixes

For each issue:

Issue:
Why it is a problem:
Suggested Fix:

Be detailed and educational.
"""
    return ask_ai(prompt)


def optimize_code(code: str) -> str:
    prompt = f"""
You are a software architect reviewing code.

Code:
{code[:12000]}

Provide:

1. Readability Improvements
2. Performance Improvements
3. Maintainability Improvements
4. Best Practice Recommendations

Then provide:

Optimized Version

with improved code.

Explain every important change.
"""
    return ask_ai(prompt)