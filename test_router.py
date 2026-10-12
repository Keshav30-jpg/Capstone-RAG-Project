# test_router.py - temporary, tests router.py logic with no API calls needed (it's all local).
from rag.router import route_message, RouteType

test_cases = [
    ("hi", False, RouteType.GREETING),
    ("hello there", False, RouteType.GREETING),
    ("thanks!", True, RouteType.GREETING),
    ("how are you?", True, RouteType.GREETING),
    ("What does page 3 say about pricing?", False, RouteType.NO_PDF),
    ("Summarize the introduction.", False, RouteType.NO_PDF),
    ("What does page 3 say about pricing?", True, RouteType.RAG),
    ("hi, what does the document say about refunds?", True, RouteType.RAG),  # tricky case
]

passed = 0
for message, has_pdf, expected in test_cases:
    result = route_message(message, has_pdf)
    status = "✅" if result == expected else "❌"
    if result == expected:
        passed += 1
    print(f"{status}  \"{message}\"  (has_pdf={has_pdf})  ->  got={result.value}  expected={expected.value}")

print(f"\n{passed}/{len(test_cases)} passed")