# SAP FI 결산 프로세스 가이드

## 1. 월말 결산 순서 (Closing Sequence)

| 순서 | 작업 | T-Code | 담당 |
|------|------|--------|------|
| 1 | 미결 전표 확인 | FBL3N | FI팀 |
| 2 | 감가상각 계산/전기 | AFAB | AA팀 |
| 3 | GR/IR 정리 | F.13 | MM/FI팀 |
| 4 | 외화 평가 | F.05 | FI팀 |
| 5 | 원가 결산 | KO8G | CO팀 |
| 6 | 손익 이전 | F.01 | FI팀 |
| 7 | 재무제표 검증 | F.01 / S_ALR_87012284 | 재무팀 |
| 8 | 기간 잠금 | OB52 | FI팀 |

---

## 2. 외화 평가 (F.05) 설정

### 평가 방법
- **KTO Method**: 미실현 손익 + 상계 전표 자동 생성
- **평가 Run 순서**: AR → AP → Bank → GL

### 주의사항
- 평가 후 역전 전표(Reverse) 생성 확인 필수
- 평가기준일: 월말 영업일 기준 (자사: 매월 마지막 영업일)
- 환율 기준: 회사 내부 환율 테이블 (OB08) 사전 등록 필요

---

## 3. 감가상각 (AFAB) 실행 절차

```
AFAB 실행 (Test Run)
    │
    ▼
결과 검증 (예상 감가상각비 확인)
    │
    ▼
AFAB 실행 (Production Run)
    │
    ▼
AW01N으로 자산별 감가상각 확인
    │
    ▼
S_ALR_87011963 감가상각 보고서 출력
```

### 재실행 시 주의
- 동일 기간 재실행: "Repeat" 옵션 선택
- 오류 발생 시: AFBD (감가상각 재설정) 후 재실행

---

## 4. GR/IR 계정 정리 (F.13)

### GR/IR 불일치 유형
| 유형 | 원인 | 조치 |
|------|------|------|
| GR 완료 / IR 미수취 | 송장 미도착 | 송장 수취 후 MIRO |
| IR 완료 / GR 미완료 | 입고 누락 | MIGO 입고 처리 |
| 수량 차이 | 부분 입고 | 잔여 수량 처리 또는 PO 수정 |

---

## 5. 기간 마감 잠금 (OB52)

### 기간 설정 구조
```
Account Type  |  Period 1 From/To  |  Period 2 From/To
A (Asset)     |  현재 기간         |  다음 기간
D (Customer)  |  현재 기간         |  다음 기간
K (Vendor)    |  현재 기간         |  다음 기간
S (GL)        |  현재 기간         |  다음 기간
```

### 특별기간 (Special Periods 13-16)
- Period 13: 연말 감사 조정
- Period 14-16: 세무 조정용

---

## 6. 자주 발생하는 결산 오류

### 오류 1: "Posting period not open"
**해결**: OB52에서 해당 기간 오픈 확인

### 오류 2: "Balance not zero for profit center"
**해결**: KE5T (Profit Center 대사) 실행 후 불일치 항목 수정

### 오류 3: "No exchange rate for currency pair"
**해결**: OB08에서 해당 통화쌍 환율 등록
