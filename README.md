# 🏦 SAP FI/TR Intelligent Operations Assistant

> **ITO 엔지니어를 위한 로컬 구동형 AI 업무 보조 도구**  
> 폐쇄망 환경의 SAP FI/TR 운영 지원 | 외부망 개인 노트북 전용

---

## 주요 기능

### 📥 Tab 1 — Data Ingestion & Masking
- **ABAP 소스 마스킹**: `ZFI_*`, `ZTR_*`, 회사코드, 금액, 계좌번호 등 자동 비식별화 후 `knowledge-base/`에 저장
- **업무 노트 저장**: 자유 형식 메모를 `YYYYMMDD_HHMMSS_work_note.md`로 즉시 저장

### 💬 Tab 2 — AI Strategic Chat
- **Google Gemini** 기반 SAP FI/TR 전문 AI 답변
- `knowledge-base/` 파일을 **1순위 참조**, 부족 시 SAP 표준 지식으로 보완
- 계열사 특화 로직 불확실 시 명확한 확인 권고

### 🔒 보안 게이트
- 보안 서약 체크박스 미확인 시 모든 기능 비활성화
- `.env` / `secrets.toml` / `knowledge-base/` 개인 노트는 `.gitignore`로 git 추적 제외

---

## 빠른 시작

```powershell
# 1. 패키지 설치
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. API 키 설정 (PowerShell)
$env:GOOGLE_API_KEY = "AIza..."

# 3. 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| UI | Streamlit + Custom Dark CSS |
| AI | Google Gemini 2.0 Flash Lite (`google-genai` SDK) |
| 지식베이스 | 로컬 `knowledge-base/*.md` 키워드 검색 |
| 마스킹 | Python `re` 정규표현식 8종 규칙 |
| MCP | `mcp_server.py` (Model Context Protocol 로컬 서버) |

---

## 파일 구조

```
.
├── app.py                  # Streamlit 메인 앱
├── mcp_server.py           # MCP 로컬 지식베이스 서버
├── requirements.txt        # 패키지 목록
├── mcp_config.json         # MCP 서버 설정
├── .streamlit/
│   └── config.toml         # 다크 테마 설정
└── knowledge-base/         # 개인 업무 노트 (git 미추적)
    ├── YYYYMMDD_HHMMSS_abap_masked.md
    └── YYYYMMDD_HHMMSS_work_note.md
```

---

## 보안 주의사항

- ❌ `GOOGLE_API_KEY`를 코드에 하드코딩하지 마세요
- ❌ `knowledge-base/` 내 실제 업무 노트는 원격 저장소에 올리지 마세요
- ✅ API 키는 환경변수 또는 `.env` 파일(`.gitignore` 처리)로 관리하세요

---

*SAP FI/TR Intelligent Operations Assistant v2.0.0*
