"""
SAP FI/TR Intelligent Operations Assistant
============================================
Version : 2.0.0
Purpose : 2-Tab 구조 — Data Ingestion & Masking / AI Strategic Chat
          폐쇄망 ITO 엔지니어 외부망 전용 도구
"""

import os
import re
import datetime
from pathlib import Path

import streamlit as st

# ──────────────────────────────────────────────────────────────
# 1. Page Config  (반드시 첫 번째 Streamlit 호출)
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAP FI/TR Ops Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────
# 2. IDE-Style Dark CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ═══ RESET / BASE ═══════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
    font-family: 'Segoe UI', 'Malgun Gothic', 'Noto Sans KR', sans-serif;
}

/* ═══ HIDE SIDEBAR TOGGLE ════════════════════════════════ */
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"]  { display: none !important; }

/* ═══ HEADER STRIP ══════════════════════════════════════ */
.app-header {
    background: linear-gradient(90deg, #0d1117 0%, #161b22 100%);
    border-bottom: 1px solid #21262d;
    padding: 0.9rem 1.4rem 0.7rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.2rem;
}
.app-header h1 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #58a6ff !important;
    margin: 0;
}
.app-header .sub {
    font-size: 0.75rem;
    color: #8b949e;
    margin: 0;
}
.badge-warn {
    background: #2d1a00;
    border: 1px solid #d29922;
    border-radius: 4px;
    padding: 2px 10px;
    font-size: 0.72rem;
    color: #e3b341;
    margin-left: auto;
    white-space: nowrap;
}

/* ═══ TABS ══════════════════════════════════════════════ */
div[data-baseweb="tab-list"] {
    background: #161b22 !important;
    border-bottom: 1px solid #21262d !important;
    gap: 0 !important;
}
button[data-baseweb="tab"] {
    background: transparent !important;
    color: #8b949e !important;
    font-size: 0.88rem;
    font-weight: 500;
    padding: 0.6rem 1.4rem !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
}
button[data-baseweb="tab"]:hover { color: #c9d1d9 !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    color: #58a6ff !important;
    border-bottom: 2px solid #1f6feb !important;
    background: transparent !important;
}
div[data-testid="stTabContent"] { padding-top: 1rem !important; }

/* ═══ INPUTS / TEXTAREAS ════════════════════════════════ */
textarea, input[type="text"], input[type="password"] {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    font-family: 'Consolas', 'Cascadia Code', monospace !important;
    font-size: 0.83rem !important;
}
textarea:focus, input:focus {
    border-color: #1f6feb !important;
    box-shadow: 0 0 0 2px rgba(31,111,235,0.22) !important;
}
div[data-baseweb="textarea"] { background: transparent !important; }
label[data-testid="stWidgetLabel"],
div[data-testid="stTextInput"] label { color: #8b949e !important; font-size: 0.8rem !important; }

/* ═══ BUTTONS ═══════════════════════════════════════════ */
div.stButton > button {
    background: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 0.38rem 1rem;
    font-size: 0.83rem;
    font-weight: 500;
    transition: all 0.15s ease;
}
div.stButton > button:hover {
    background: #1f6feb;
    border-color: #1f6feb;
    color: #fff;
}
div.stButton > button[kind="primary"] {
    background: #1f6feb !important;
    border-color: #1f6feb !important;
    color: #fff !important;
}
div.stButton > button[kind="primary"]:hover {
    background: #388bfd !important;
    border-color: #388bfd !important;
}

/* ═══ MASKED CODE OUTPUT ════════════════════════════════ */
.code-out {
    background: #0d1117;
    border: 1px solid #3fb950;
    border-radius: 6px;
    padding: 0.9rem 1rem;
    font-family: 'Consolas', 'Cascadia Code', monospace;
    font-size: 0.8rem;
    color: #3fb950;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 320px;
    overflow-y: auto;
    line-height: 1.55;
    margin-top: 0.5rem;
}

/* ═══ SECTION LABEL ══════════════════════════════════════ */
.sec-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.45rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid #21262d;
}

/* ═══ FILE CHIPS ════════════════════════════════════════ */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 2px 9px;
    font-size: 0.73rem;
    color: #8b949e;
    margin-right: 4px;
    margin-bottom: 3px;
}
.chip.green { border-color: #3fb950; color: #3fb950; background: #0d1f12; }
.chip.blue  { border-color: #1f6feb; color: #58a6ff; background: #0d1a2e; }

/* ═══ CHAT BUBBLES ══════════════════════════════════════ */
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    max-height: 55vh;
    overflow-y: auto;
    padding: 0.4rem 0.1rem 0.6rem;
    margin-bottom: 0.8rem;
}
.msg-user {
    align-self: flex-end;
    max-width: 74%;
    background: #1a3a5c;
    border: 1px solid #1f6feb;
    border-radius: 10px 10px 2px 10px;
    padding: 0.6rem 0.85rem;
    font-size: 0.87rem;
    color: #cae8ff;
    line-height: 1.55;
    white-space: pre-wrap;
}
.msg-ai {
    align-self: flex-start;
    max-width: 91%;
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px 10px 10px 2px;
    padding: 0.7rem 0.9rem;
    font-size: 0.87rem;
    color: #c9d1d9;
    line-height: 1.68;
    white-space: pre-wrap;
}
.msg-ts {
    font-size: 0.68rem;
    color: #484f58;
    margin-top: 4px;
}
.msg-sources {
    font-size: 0.72rem;
    color: #8b949e;
    border-top: 1px solid #21262d;
    margin-top: 0.45rem;
    padding-top: 0.35rem;
}
.empty-chat {
    text-align: center;
    padding: 2.5rem 0;
    color: #484f58;
    font-size: 0.88rem;
}

/* ═══ METRICS ════════════════════════════════════════════ */
div[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 0.5rem;
}
div[data-testid="stMetricValue"] { color: #58a6ff !important; font-size: 1rem !important; }
div[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 0.75rem !important; }

/* ═══ ALERTS ════════════════════════════════════════════ */
div[data-testid="stAlert"] {
    background: #161b22 !important;
    border-radius: 6px;
    font-size: 0.85rem;
}

/* ═══ HINT CHIPS ROW ════════════════════════════════════ */
.hints { margin-top: 0.6rem; }
.hint-chip {
    display: inline-block;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 3px 12px;
    font-size: 0.75rem;
    color: #8b949e;
    margin-right: 6px;
    margin-bottom: 4px;
}

/* ═══ SCROLLBAR ══════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #484f58; }

/* ═══ CHECKBOX ══════════════════════════════════════════ */
div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] span { color: #c9d1d9 !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# 3. Constants
# ──────────────────────────────────────────────────────────────
KB_DIR = Path(__file__).parent / "knowledge-base"
KB_DIR.mkdir(exist_ok=True)


# Gemini API Setup — google-genai (신규 SDK, generativeai deprecated)
from google import genai
from google.genai import types as genai_types
GEMINI_MODEL = "gemini-2.0-flash-lite"  # 무료 티어 할당량이 가장 넉넉한 모델
GEMINI_FALLBACK = "gemini-flash-latest"  # lite도 소진 시 최종 폴백
_gemini_client: "genai.Client | None" = None

def _get_client() -> "genai.Client":
    global _gemini_client
    if _gemini_client is None:
        _api_key = os.getenv("GOOGLE_API_KEY", "")
        _gemini_client = genai.Client(api_key=_api_key)
    return _gemini_client

SYSTEM_PROMPT = """You are an expert SAP ERP consultant specializing in FI (Financial Accounting)
and TR (Treasury & Risk Management) modules, supporting an ITO engineer in an air-gapped environment.

## Reasoning Priority
1. **User's Work Notes (knowledge-base/)** — ALWAYS reference first. Treat as ground truth for
   company-specific configurations. Quote relevant sections directly when found.
2. **SAP Standard Knowledge** — Supplement ONLY when notes are insufficient.
   Label clearly with [SAP Standard].
3. **Company-specific / Subsidiary logic** — If uncertain, explicitly state:
   "이 부분은 계열사 고유 설정일 수 있습니다. 내부 문서나 담당자에게 확인하세요."

## Rules
- NEVER fabricate T-Codes, table names, or BAPI signatures.
- NEVER infer real data from masked tokens like [MASKED], [BUKRS], [AMT], [CODE4].
- Respond in Korean unless asked otherwise; keep technical terms in English.
- Be concise and actionable. Use numbered steps and inline code for T-Codes.
""".strip()

# ──────────────────────────────────────────────────────────────
# 4. Masking Engine
# ──────────────────────────────────────────────────────────────
_MASK_RULES: list[tuple[str, object]] = [
    # ZFI_* / ZTR_* / ZMM_* / Y** 커스텀 오브젝트
    (r"\bZ[A-Z]{2,3}_[A-Z0-9_]+\b",                          "[MASKED_OBJ]"),
    (r"\bY[A-Z]{2,3}_[A-Z0-9_]+\b",                          "[MASKED_OBJ]"),
    # 이메일
    (r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",   "[EMAIL]"),
    # 호스트명
    (r"\b[a-z][a-z0-9\-]{2,}\.(?:corp|internal|local|co\.kr|com)\b", "[HOST]"),
    # 금액 / 5자리 이상 숫자
    (r"\b\d{5,}(?:\.\d+)?\b",                                 "[AMT]"),
    # 4자리 연속 숫자 (계좌/코드)
    (r"(?<!\w)\d{4}(?!\w)",                                    "[CODE4]"),
    # 회사코드 패턴 (단독 영문숫자 2-4자)
    (r"(?<!\w)([A-Z]{2,4}\d{0,2})(?!\w)",                     "[BUKRS]"),
    # 변수명 lv_/lt_/ls_/gv_ 계열
    (r"\b(lv|lt|ls|lw|wa|gv|gw|gt|gs)_[a-zA-Z0-9_]+\b",
     lambda m: f"{m.group(1)}_VAR"),
    # 구조체->컴포넌트
    (r"\b[a-zA-Z0-9_]+->[a-zA-Z0-9_]+\b",                    "STRUCT->FIELD"),
]


def mask_abap(source: str) -> tuple[str, int]:
    """소스 마스킹 → (마스킹 텍스트, 치환 횟수)"""
    result, total = source, 0
    for pattern, repl in _MASK_RULES:
        if callable(repl):
            result, n = re.subn(pattern, repl, result)
        else:
            result, n = re.subn(pattern, repl, result)
        total += n
    return result, total


# ──────────────────────────────────────────────────────────────
# 5. Knowledge Base I/O
# ──────────────────────────────────────────────────────────────

def kb_save(content: str, kind: str) -> Path:
    """YYYYMMDD_HHMMSS_kind.md 형식으로 저장"""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fp = KB_DIR / f"{ts}_{kind}.md"
    fp.write_text(content, encoding="utf-8")
    return fp


def kb_load_all() -> dict[str, str]:
    """knowledge-base/ 내 모든 .md / .txt 로드"""
    docs: dict[str, str] = {}
    for ext in ("*.md", "*.txt"):
        for fp in sorted(KB_DIR.glob(ext)):
            try:
                docs[fp.name] = fp.read_text(encoding="utf-8")
            except Exception:
                pass
    return docs


def kb_search(query: str, docs: dict[str, str], top_k: int = 4) -> list[dict]:
    """키워드 기반 관련도 검색 → 상위 top_k 결과"""
    tokens = set(re.findall(r"[가-힣a-zA-Z0-9_/]{2,}", query.lower()))
    if not tokens:
        return []
    scored: list[tuple[float, str, str]] = []
    for name, text in docs.items():
        tl = text.lower()
        hits = sum(1 for t in tokens if t in tl)
        if hits:
            scored.append((hits / len(tokens), name, text))
    scored.sort(reverse=True)

    results = []
    for score, name, text in scored[:top_k]:
        tl = text.lower()
        best_pos, best_n = 0, 0
        for i in range(0, max(1, len(text) - 300), 60):
            n = sum(1 for t in tokens if t in tl[i: i + 300])
            if n > best_n:
                best_n, best_pos = n, i
        results.append({
            "name": name,
            "score": round(score, 3),
            "excerpt": text[best_pos: best_pos + 300].strip(),
        })
    return results


def kb_build_context(hits: list[dict]) -> str:
    if not hits:
        return ""
    parts = ["## 참조된 업무 노트 (knowledge-base)\n"]
    for h in hits:
        parts.append(
            f"### [{h['name']}]  score={h['score']}\n"
            f"```\n{h['excerpt']}\n```\n"
        )
    return "\n".join(parts)


# ──────────────────────────────────────────────────────────────
# 6. Claude API Call
# ──────────────────────────────────────────────────────────────

def call_gemini(messages: list[dict], context_block: str) -> str:
    """Google Gemini 호출 (google-genai 신규 SDK)
    - 429 할당량 초과 시 폴백 모델로 자동 전환
    - system_instruction은 GenerateContentConfig에 주입
    """
    _api_key = os.getenv("GOOGLE_API_KEY", "")
    if not _api_key:
        return (
            "⚠️ **GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.**\n\n"
            "```powershell\n$env:GOOGLE_API_KEY = 'AIza...'\nstreamlit run app.py\n```"
        )

    client = _get_client()
    full_system = SYSTEM_PROMPT + (f"\n\n{context_block}" if context_block else "")

    # 대화 이력 → Contents 리스트 변환
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append(
            genai_types.Content(
                role=role,
                parts=[genai_types.Part(text=m["content"])],
            )
        )

    config = genai_types.GenerateContentConfig(
        system_instruction=full_system,
        temperature=0.3,
        max_output_tokens=2048,
    )

    # 모델 순서대로 시도: 기본 → 폴백
    for model_name in (GEMINI_MODEL, GEMINI_FALLBACK):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
            return response.text
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                # 재시도 대기시간 파싱
                import re as _re
                wait_match = _re.search(r"retry.*?(\d+)s", err_str, _re.IGNORECASE)
                wait_sec = wait_match.group(1) if wait_match else "잠시"
                if model_name == GEMINI_FALLBACK:
                    # 모든 폴백 소진
                    return (
                        f"⚠️ **API 할당량 초과 (429)**\n\n"
                        f"모든 모델(`{GEMINI_MODEL}`, `{GEMINI_FALLBACK}`)의 무료 티어 한도가 소진되었습니다.\n\n"
                        f"**해결 방법:**\n"
                        f"1. **{wait_sec}초 후 다시 시도**하세요.\n"
                        f"2. [Google AI Studio](https://aistudio.google.com/apikey)에서 **결제 계정 연결** (유료 플랜 전환)\n"
                        f"3. 또는 내일(일일 한도 리셋) 재시도\n\n"
                        f"> 💡 무료 플랜 한도: gemini-2.0-flash 기준 분당 15회, 일일 1,500회"
                    )
                # 다음 폴백 모델로 전환
                continue
            else:
                return f"❌ API 오류: {e}"

    return "❌ 알 수 없는 오류가 발생했습니다."


# ──────────────────────────────────────────────────────────────
# 7. Session State Init
# ──────────────────────────────────────────────────────────────
for _k, _v in {
    "oath": False,
    "chat": [],
    "masked_preview": "",
    "mask_count": 0,
    "clear_note": False,      # 노트 저장 후 입력창 초기화 플래그
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# 노트 초기화 플래그 처리 — rerun 직후 위젯 렌더 전에 값을 비움
if st.session_state.get("clear_note"):
    st.session_state["note_title"] = ""
    st.session_state["note_body"] = ""
    st.session_state["clear_note"] = False

# ──────────────────────────────────────────────────────────────
# 8. App Header
# ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <span style="font-size:1.55rem;line-height:1">🏦</span>
    <div>
        <h1>SAP FI/TR Intelligent Operations Assistant</h1>
        <p class="sub">ITO Engineer Support Tool &nbsp;·&nbsp; Local-First &nbsp;·&nbsp; Air-Gap Ready</p>
    </div>
    <span class="badge-warn">⚠ 외부망 전용 — 내부 기밀 입력 금지</span>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# 9. Security Oath  (전체 페이지 게이트)
# ──────────────────────────────────────────────────────────────
st.session_state.oath = st.checkbox(
    "🔒 **보안 서약 확인** — 고객사 기밀정보·내부 접속정보가 포함되지 않았음을 확인합니다.",
    value=st.session_state.oath,
    key="oath_chk",
)

if not st.session_state.oath:
    st.warning("보안 서약을 확인해야 저장 및 채팅 기능이 활성화됩니다.", icon="🔒")
    st.stop()

# ── 상태 지표 ─────────────────────────────────────────────────
kb_files_all = sorted(KB_DIR.glob("*.md")) + sorted(KB_DIR.glob("*.txt"))
c1, c2, c3, c4 = st.columns(4)
c1.metric("📂 저장된 노트", len(kb_files_all))
c2.metric("🤖 모델", GEMINI_MODEL)
c3.metric("🔑 API Key", "✅ 설정됨" if os.getenv("GOOGLE_API_KEY") else "❌ 미설정")
c4.metric("💬 대화 턴", len(st.session_state.chat) // 2)

# ──────────────────────────────────────────────────────────────
# 10. Tabs
# ──────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs([
    "📥  Tab 1 — Data Ingestion & Masking",
    "💬  Tab 2 — AI Strategic Chat",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 ─ Data Ingestion & Masking
# ══════════════════════════════════════════════════════════════
with tab1:
    left, right = st.columns(2, gap="large")

    # ── 왼쪽: ABAP Source Code Masking ───────────────────────
    with left:
        st.markdown('<div class="sec-label">🔐 Source Code — ABAP 마스킹 저장</div>',
                    unsafe_allow_html=True)

        abap_src = st.text_area(
            "ABAP 소스",
            height=300,
            placeholder=(
                "* 내부망 ABAP 소스를 붙여넣으세요.\n"
                "* ZFI_*, ZTR_*, 회사코드, 금액 등이 자동 마스킹됩니다.\n\n"
                "DATA: lv_bukrs TYPE bukrs VALUE 'KR01',\n"
                "      lv_amount TYPE waers.\n\n"
                "SELECT * FROM ZFI_CUSTOM_DOC\n"
                "  INTO TABLE lt_docs\n"
                " WHERE bukrs = lv_bukrs\n"
                "   AND amount > 1000000."
            ),
            label_visibility="collapsed",
            key="abap_input",
        )

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🔍 미리보기", use_container_width=True, key="btn_prev"):
                if abap_src.strip():
                    st.session_state.masked_preview, st.session_state.mask_count = mask_abap(abap_src)
                else:
                    st.toast("소스코드를 먼저 입력하세요.", icon="⚠️")
        with b2:
            if st.button("💾 마스킹 후 저장", use_container_width=True,
                         type="primary", key="btn_msave"):
                if abap_src.strip():
                    masked, cnt = mask_abap(abap_src)
                    header = (
                        f"# ABAP Masked Source\n"
                        f"> 저장: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
                        f"/ 마스킹 {cnt}건\n\n"
                        f"```abap\n{masked}\n```\n"
                    )
                    fp = kb_save(header, "abap_masked")
                    st.session_state.masked_preview = masked
                    st.session_state.mask_count = cnt
                    st.toast(f"✅ 저장 완료 → {fp.name}", icon="💾")
                else:
                    st.toast("소스코드를 먼저 입력하세요.", icon="⚠️")

        # 마스킹 결과 출력
        if st.session_state.masked_preview:
            st.markdown(
                f'<div class="sec-label" style="margin-top:.9rem">'
                f'마스킹 결과 — {st.session_state.mask_count}건 치환</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="code-out">{st.session_state.masked_preview}</div>',
                unsafe_allow_html=True,
            )
            st.download_button(
                "⬇️ 결과 다운로드",
                data=st.session_state.masked_preview,
                file_name=f"masked_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt",
                mime="text/plain",
            )

        # 마스킹 규칙 참조
        with st.expander("📋 마스킹 규칙 참조", expanded=False):
            st.markdown("""
| 대상 | 예시 | 결과 |
|---|---|---|
| 커스텀 오브젝트 | `ZFI_PAYMENT`, `ZTR_HEDGE` | `[MASKED_OBJ]` |
| 이메일 | `user@corp.co.kr` | `[EMAIL]` |
| 호스트명 | `sapdev.corp.co.kr` | `[HOST]` |
| 금액 (5자리↑) | `1000000` | `[AMT]` |
| 4자리 코드 | `1234` | `[CODE4]` |
| 회사코드 | `KR01`, `ABCD` | `[BUKRS]` |
| 변수명 | `lv_amount`, `lt_docs` | `lv_VAR`, `lt_VAR` |
| 구조체→필드 | `ls_doc->bukrs` | `STRUCT->FIELD` |
""")

    # ── 오른쪽: Work Notes ────────────────────────────────────
    with right:
        st.markdown('<div class="sec-label">📝 Work Notes — 업무 노트 저장</div>',
                    unsafe_allow_html=True)

        note_title = st.text_input(
            "노트 제목 (선택)",
            placeholder="예: FF7B 유동성 조회 오류 대응 절차",
            key="note_title",
        )
        note_body = st.text_area(
            "노트 내용",
            height=270,
            placeholder=(
                "자유 형식으로 업무 로직, 장애 대응 메모,\n"
                "트랜잭션 절차 등을 기록하세요.\n\n"
                "예시:\n"
                "## FF7B 유동성 예측 오류\n"
                "증상: Planning Level 미조회\n"
                "원인: TR20 매핑 누락\n"
                "조치: TR20 → Bank Account → Level 재연결"
            ),
            key="note_body",
            label_visibility="collapsed",
        )

        if st.button("📌 노트 저장", use_container_width=True,
                     type="primary", key="btn_nsave"):
            if note_body.strip():
                title_md = f"# {note_title.strip()}\n\n" if note_title.strip() else ""
                body = (
                    f"{title_md}"
                    f"> 저장: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"{note_body.strip()}"
                )
                fp = kb_save(body, "work_note")
                st.toast(f"✅ 저장 완료 → {fp.name}", icon="📌")
                # 위젯 key 바인딩된 값은 같은 사이클에서 직접 수정 불가
                # → 플래그 세우고 rerun 후 다음 사이클 상단에서 초기화
                st.session_state["clear_note"] = True
                st.rerun()
            else:
                st.toast("노트 내용을 입력하세요.", icon="⚠️")

        # ── 저장된 파일 목록 ──────────────────────────────────
        st.markdown(
            '<div class="sec-label" style="margin-top:1.1rem">📂 저장된 파일 목록</div>',
            unsafe_allow_html=True,
        )
        current_files = sorted(
            list(KB_DIR.glob("*.md")) + list(KB_DIR.glob("*.txt")),
            reverse=True,
        )
        if current_files:
            for fp in current_files[:15]:
                kind = "abap_masked" if "abap_masked" in fp.name else "work_note"
                badge = (
                    '<span class="chip green">ABAP</span>'
                    if kind == "abap_masked"
                    else '<span class="chip blue">NOTE</span>'
                )
                size_kb = fp.stat().st_size / 1024
                st.markdown(
                    f'{badge} <code style="font-size:.78rem;color:#8b949e">{fp.name}</code> '
                    f'<span style="color:#484f58;font-size:.72rem">{size_kb:.1f} KB</span>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<p style="color:#484f58;font-size:.82rem;margin:0">'
                "저장된 파일이 없습니다.</p>",
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════
# TAB 2 ─ AI Strategic Chat
# ══════════════════════════════════════════════════════════════
with tab2:

    # ── 대화 내역 렌더링 ─────────────────────────────────────
    if st.session_state.chat:
        bubbles = []
        for msg in st.session_state.chat:
            ts = msg.get("ts", "")
            role = msg["role"]
            # HTML 이스케이프
            safe = (
                msg["content"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            if role == "user":
                bubbles.append(
                    f'<div class="msg-user">{safe}'
                    f'<div class="msg-ts">{ts}</div></div>'
                )
            else:
                src_html = ""
                if msg.get("sources"):
                    items = "  ·  ".join(
                        f'<code style="font-size:.72rem">{s}</code>'
                        for s in msg["sources"]
                    )
                    src_html = f'<div class="msg-sources">📚 참조: {items}</div>'
                bubbles.append(
                    f'<div class="msg-ai">{safe}'
                    f'{src_html}'
                    f'<div class="msg-ts">{ts}</div></div>'
                )
        st.markdown(
            '<div class="chat-wrap">' + "".join(bubbles) + "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="empty-chat">'
            '🤖 SAP FI/TR 관련 질문을 입력하세요.<br>'
            '<span style="font-size:.78rem;color:#30363d">'
            'knowledge-base/ 파일을 1순위로 참조합니다.'
            '</span></div>',
            unsafe_allow_html=True,
        )

    # ── 입력창 + 버튼 ─────────────────────────────────────────
    q_col, send_col, clr_col = st.columns([7, 1, 1], gap="small")
    with q_col:
        user_input = st.text_input(
            "질문",
            placeholder="예: FF7B에서 유동성 예측이 조회되지 않는 원인과 해결방법은?",
            label_visibility="collapsed",
            key="chat_input",
        )
    with send_col:
        do_send = st.button("전송 ▶", use_container_width=True,
                            type="primary", key="btn_send")
    with clr_col:
        if st.button("초기화", use_container_width=True, key="btn_clr"):
            st.session_state.chat = []
            st.rerun()

    # ── 전송 처리 ─────────────────────────────────────────────
    if do_send and user_input.strip():
        ts_now = datetime.datetime.now().strftime("%H:%M:%S")

        # 1) 사용자 메시지 등록
        st.session_state.chat.append({
            "role": "user",
            "content": user_input.strip(),
            "ts": ts_now,
        })

        # 2) KB 검색
        docs = kb_load_all()
        hits = kb_search(user_input, docs, top_k=4)
        ctx = kb_build_context(hits)
        sources = [h["name"] for h in hits]

        # 3) 이력 구성 (최근 20메시지 = 10턴)
        history: list[dict] = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.chat[-20:]
            if m["role"] in ("user", "assistant")
        ]

        # 4) Claude 호출
        with st.spinner("🤖 분석 중…"):
            reply = call_gemini(history, ctx)

        # 5) 응답 저장
        st.session_state.chat.append({
            "role": "assistant",
            "content": reply,
            "ts": datetime.datetime.now().strftime("%H:%M:%S"),
            "sources": sources,
        })
        st.rerun()

    # ── 힌트 칩 (대화 없을 때) ─────────────────────────────────
    if not st.session_state.chat:
        hints = [
            "FF7B 유동성 예측", "F110 Payment Run",
            "F.05 외화 평가", "FEBA 은행 대사",
            "OB52 기간 마감", "AFAB 감가상각",
            "MIRO 송장 처리", "FBL3N 명세 조회",
        ]
        chips = "".join(f'<span class="hint-chip">{h}</span>' for h in hints)
        st.markdown(f'<div class="hints">{chips}</div>', unsafe_allow_html=True)
