"""
Standalone test for the MCI LLM analyzer (Task 3).

Runs without network: it injects a fake `requests` module so the MCI REST call
is captured and canned responses are returned. Exits non-zero on failure.

Run from the repo root:
    python test_scripts/test_mci_analyzer.py
"""

import asyncio
import json
import os
import sys
import types

# Make the 'src' package directory importable (packages live under src/).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# --- Fake `requests` module: a queue of responses + captured calls ---------
CALLS = []        # captured POST payloads
RESPONSES = []    # queue of (status_code, body) to return, one per call


def _fake_post(url, headers=None, json=None, timeout=None):
    CALLS.append({"url": url, "headers": headers, "json": json})
    status, body = RESPONSES.pop(0)

    class _Resp:
        def __init__(self):
            self.status_code = status
            self.ok = status < 400
            self.text = body if isinstance(body, str) else __import__("json").dumps(body)

        def json(self):
            import json as _j
            return body if isinstance(body, dict) else _j.loads(body)

    return _Resp()


_fake_requests = types.ModuleType("requests")
_fake_requests.post = _fake_post
sys.modules["requests"] = _fake_requests

from llm_integration.mci_analyzer import MCIProductionAnalyzer  # noqa: E402

SAMPLE = {
    "machines": [
        {"name": "Schleifmaschine1", "status": "ERROR", "cycle_time": 2.5,
         "error_rate": 0.02, "produced": 360, "oee": 54.2},
    ],
    "buffers": [
        {"name": "Buffer2", "fill_level": 98.0, "capacity": 100, "overflow": 37},
    ],
    "kpis": {"oee": 74.0, "throughput": 118.5, "scrap_rate": 2.1, "utilization": 76.4},
    "raw_stock": 8200,
    "finished_stock": 342,
    "simulation_time": 100.0,
}

ANALYSIS_JSON = json.dumps({"analysis": {"bottleneck": "Schleifmaschine1"},
                            "parameter_suggestions": {}})


def _body(content, tokens=123):
    return {"data": {"content": content, "usage": {"totalTokens": tokens}}}


def _fresh(**kw):
    return MCIProductionAnalyzer(api_key="id", api_secret="sec", **kw)


def test_uses_only_user_role_and_parses_plain_json():
    CALLS.clear(); RESPONSES.clear()
    RESPONSES.append((200, _body(ANALYSIS_JSON)))
    a = _fresh(model="gpt-4o")
    result = asyncio.run(a.analyze(SAMPLE))
    assert result["analysis"]["bottleneck"] == "Schleifmaschine1", result
    roles = {m["role"] for m in CALLS[0]["json"]["messages"]}
    assert roles <= {"user", "assistant"} and "system" not in roles, roles
    assert a.last_tokens_used == 123
    print("[OK] test_uses_only_user_role_and_parses_plain_json")


def test_parses_json_in_code_fence():
    CALLS.clear(); RESPONSES.clear()
    fenced = "```json\n" + ANALYSIS_JSON + "\n```"
    RESPONSES.append((200, _body(fenced)))
    a = _fresh()
    result = asyncio.run(a.analyze(SAMPLE))
    assert result is not None, "should parse JSON wrapped in a ```json fence"
    assert result["analysis"]["bottleneck"] == "Schleifmaschine1"
    print("[OK] test_parses_json_in_code_fence")


def test_parses_json_with_surrounding_prose():
    CALLS.clear(); RESPONSES.clear()
    prose = "Hier ist die Analyse:\n" + ANALYSIS_JSON + "\nViele Grüße"
    RESPONSES.append((200, _body(prose)))
    a = _fresh()
    result = asyncio.run(a.analyze(SAMPLE))
    assert result is not None, "should extract the JSON object from prose"
    assert result["analysis"]["bottleneck"] == "Schleifmaschine1"
    print("[OK] test_parses_json_with_surrounding_prose")


def test_empty_content_records_raw_error():
    CALLS.clear(); RESPONSES.clear()
    RESPONSES.append((200, _body("")))
    a = _fresh()
    result = asyncio.run(a.analyze(SAMPLE))
    assert result is None, "empty content should yield None"
    assert a.last_error and "JSON" in a.last_error, a.last_error
    print("[OK] test_empty_content_records_raw_error")


def test_error_body_is_surfaced():
    CALLS.clear(); RESPONSES.clear()
    RESPONSES.append((400, '{"message":"API request failed","x":"boom-detail"}'))
    a = _fresh()
    result = asyncio.run(a.analyze(SAMPLE))
    assert result is None and "boom-detail" in (a.last_error or ""), a.last_error
    print("[OK] test_error_body_is_surfaced")


def test_analyze_skips_when_too_soon():
    from datetime import datetime
    CALLS.clear(); RESPONSES.clear()
    a = _fresh()
    a.last_analysis_time = datetime.now()
    result = asyncio.run(a.analyze(SAMPLE))
    assert result is None and CALLS == [], "should not call API when skipping"
    print("[OK] test_analyze_skips_when_too_soon")


if __name__ == "__main__":
    test_uses_only_user_role_and_parses_plain_json()
    test_parses_json_in_code_fence()
    test_parses_json_with_surrounding_prose()
    test_empty_content_records_raw_error()
    test_error_body_is_surfaced()
    test_analyze_skips_when_too_soon()
    print("ALL TESTS PASSED")
