SAP FI/TR 장애 대응 이력 및 운영 TIP 모음
==========================================
작성 목적: ITO 운영 중 발생한 장애/이슈 기록 및 재발 방지

[장애 #001] F110 Payment Run 후 은행 파일 미전송
발생일: -
증상: F110 Payment Run 정상 완료, 은행 전송 파일(DMEE) 미생성
원인: House Bank 설정의 Bank Account에 DME Format 미연결
조치:
  1. FI12 → House Bank → Bank Account 선택
  2. "Bank Statement" 탭에서 DME Format 코드 확인
  3. 담당 SI에게 DMEE Tree 설정 요청 (BASIS 권한 필요)
재발방지: 신규 House Bank 등록 시 체크리스트 항목 추가

[장애 #002] 월말 외화평가(F.05) 실행 오류
발생일: -
증상: F.05 실행 시 "No exchange rate found for USD/KRW" 오류
원인: OB08에 해당 월 환율 미등록
조치:
  1. OB08 → 신규 환율 입력 (Valid From = 평가기준일)
  2. 환율 타입: M (Average Rate), B (Buying Rate), G (Selling Rate)
  3. 자사 기준: 기획재정부 고시환율 사용 (매월 1일 일괄 등록)
재발방지: 매월 초 환율 등록 배치 작업 확인 (배치 JOB: ZFI_EXRATE_UPLOAD)

[장애 #003] FEBA 은행명세서 대사 불일치
발생일: -
증상: MT940 Import 후 잔액이 SAP와 10만원 불일치
원인: 전일 마감 후 당일 오전 입금 건이 전일 명세에 포함
조치:
  1. FF67 (Manual Bank Statement) → 누락 건 수동 입력
  2. BNK Posting Rule 확인: Posting Key 및 Account 설정
  3. FBL3N으로 은행계정 잔액 재확인
재발방지: 은행명세서 수신 시간 은행 담당자와 협의 (오전 8시 이전)

[운영TIP #001] FF7B 유동성 예측 조회가 느린 경우
원인: Planning Level 데이터가 많이 쌓여 있을 때
조치:
  - FDFD (Delete Liquidity Items) 로 오래된 데이터 정리
  - 조회 기간 범위를 최소화 (전체 조회 지양)

[운영TIP #002] ABAP 배치 JOB 모니터링
T-Code: SM37
- JOB 상태: Active / Finished / Cancelled / Released
- Cancelled JOB 발생 시: SM37 → JOB 선택 → Spool 확인 → 오류 메시지 분석
- 반복 오류 시: 담당 ABAP 개발자에게 SM21 (System Log) 함께 전달

[운영TIP #003] 테이블 직접 조회 방법 (긴급 시)
T-Code: SE16 / SE16N
- 주요 테이블:
  BKPF: 회계 문서 헤더
  BSEG: 회계 문서 라인
  VBAK: 판매 오더 헤더
  EKKO: 구매 오더 헤더
  LFA1: Vendor 마스터
  KNA1: Customer 마스터
  BNKA: 은행 마스터
- 주의: Production 환경에서 직접 수정 절대 금지

[운영TIP #004] 사용자 권한 오류 대응 (SU53)
증상: "You do not have authorization to..." 오류
조치:
  1. SU53 실행 (오류 발생 사용자로 로그인 후)
  2. Display Last Authorization Check → 누락 권한 오브젝트 확인
  3. 보안팀에 권한 추가 요청 (S_DEVELOP, F_BKPF_BUK 등)
  4. 긴급 시: SU01 → 임시 역할 부여 후 추후 공식 요청

[운영TIP #005] Transport Request 관리
T-Code: SE10 (Transport Request 조회/관리)
- Workbench Request: 프로그램/딕셔너리 변경사항
- Customizing Request: 설정 변경사항 (SPRO 등)
- DEV → QAS → PRD 이관 순서 준수
- 이관 전 체크: 관련 의존 오브젝트 함께 포함 여부 확인
