# SAP TR 자금관리 업무 가이드

## 1. 자금관리 주요 트랜잭션 코드

| T-Code | 기능 | 설명 |
|--------|------|------|
| FF7A | Cash Position | 당일 자금 포지션 조회 |
| FF7B | Liquidity Forecast | 유동성 예측 조회 (일/주/월) |
| FBL3N | G/L Account Line Items | 총계정원장 명세 조회 |
| F-28 | Incoming Payments | 수동 입금 처리 |
| F-53 | Outgoing Payments | 수동 출금 처리 |
| F110 | Payment Run | 자동 지급 실행 |
| FEBA | Electronic Bank Statement | 전자은행명세서 처리 |
| FF_5 | Import Bank Statement | 은행명세서 Import (MT940) |

---

## 2. 자금 결의 프로세스 (Process Flow)

```
자금 요청 (부서)
    │
    ▼
자금 결의 생성 (FI 담당자)
    │  → 내부 품의 시스템 연동 (자사 커스텀 BAdI)
    ▼
팀장/재무팀장 전자결재
    │
    ▼
지급 수단 등록 (F110 파라미터)
    │  → Payment Method: T (계좌이체), C (수표)
    ▼
Payment Run 실행 (F110)
    │  → Proposal → Payment Run → Print
    ▼
은행 파일 전송 (자금팀)
    │  → 자사 온라인뱅킹 연동 또는 수동 업로드
    ▼
은행명세서 수신 및 대사 (FEBA/FF_5)
```

---

## 3. Cash Management 설정 포인트

### 3.1 Planning Level (계획 레벨)
- **B0**: 은행 잔액 (실제)
- **F0**: 미결 지급 (AP)
- **E0**: 미결 수취 (AR)
- **P0**: 자금 계획 (수동 입력)

### 3.2 Value Date 관리
- 수표 지급: 발행일 + 3 영업일
- 계좌이체: 당일 또는 익일
- 외화 결제: Spot date (T+2) 기준

---

## 4. 자금 마감 체크리스트 (월말)

- [ ] 전월 미결 은행명세서 전표 처리 완료
- [ ] Cash Position vs 실제 은행잔액 대사
- [ ] 외화 환산 평가 (F.05) 실행
- [ ] TR-CM → FI 전기 완료 확인
- [ ] 유동성 계획 보고서 재무팀 제출

---

## 5. 주요 장애 유형 및 대응

### 장애 1: F110 Payment Run 후 은행 파일 미생성
**원인**: DMEE 설정 오류 또는 House Bank 미설정  
**조치**: FI12 → House Bank → Bank Account 설정 확인

### 장애 2: FEBA 은행명세서 잔액 불일치
**원인**: 전일 미처리 전표 존재  
**조치**: FBL3N → Clearing 미완료 항목 확인 후 F-03 수동 대사

### 장애 3: FF7B 조회 시 자금 포지션 누락
**원인**: Planning Level 미설정 또는 Bank Account 연결 누락  
**조치**: TR20 → Cash Management → Planning Level 매핑 확인
