# 프로젝트 개요

이 프로젝트는 두 개의 Streamlit 대시보드 애플리케이션으로 구성되어 있습니다.

## 애플리케이션

### 1. test.py - Oracle Alert Log 분석기
- **포트**: 8502
- **설명**: Oracle 데이터베이스 Alert Log를 분석하는 웹 기반 도구
- **기능**:
  - Alert Log 텍스트 입력으로 Oracle 에러 코드 자동 추출
  - 에러 코드별 상세 정보 제공 (원인, 조치 방법, 한영 병행)
  - 크리티컬 에러 강조 표시
  - 에러 코드 검색 및 필터링
  - Oracle 공식 문서 링크 제공
- **외부 의존성**: 없음 (독립 실행 가능)
- **실행 명령어**:
  ```powershell
  streamlit run test.py --server.port 8502
  ```

### 2. app.py - DB 모니터링 대시보드
- **포트**: 8501 (로컬) / Streamlit Cloud (배포)
- **설명**: 데이터베이스 성능 지표를 실시간으로 모니터링하는 대시보드
- **기능**:
  - CPU 사용률 추이 시각화
  - Active Session 수 모니터링
  - Lock Session 수 추적
  - Alert 로그 개수 분석
  - 날짜/시간 범위 필터링
  - DB별 선택적 모니터링
  - 데이터 CSV 다운로드
  - Claude AI를 이용한 자동 요약 (1000자 이내)
  - 조회 가능 기간 표시
  - 그래프 x축 동적 포맷 (1일 이내: 시간, 2일 이상: 자정 날짜 표시)
  - **📺 홈앤쇼핑 TV 편성표 (신규)**
    - PROD_DB 선택 시에만 표시
    - 차트 hover 시 방송 정보 표시 (프로그램, 상품, 가격, 진행자)
    - 시간대 범위 매칭 (start_time ~ end_time)
    - TV 편성표 데이터 조회 및 CSV 다운로드
- **외부 의존성**: Supabase 데이터베이스 (필수), Anthropic Claude API (선택)
- **실행 명령어**:
  ```powershell
  streamlit run app.py --server.port 8501
  ```

## 설치 및 실행

### 필수 패키지 설치
```powershell
pip install -r requirements.txt
```

또는 개별 설치:
```powershell
pip install streamlit pandas plotly numpy supabase anthropic httpx python-dotenv
```

### Supabase 설정 (app.py용)

1. Supabase 프로젝트 생성 (https://supabase.com)
2. `dba_monitoring` 테이블 생성 (아래 스키마 참고)
3. CSV 데이터를 Supabase 테이블에 업로드
4. `.streamlit/secrets.toml` 파일 생성:
   ```toml
   supabase_url = "https://[PROJECT_ID].supabase.co"
   supabase_key = "your_anon_public_key"
   anthropic_api_key = "your_anthropic_api_key"
   ```
5. `.gitignore`에 `.streamlit/secrets.toml` 추가 (API key 보안)

### 로컬 동시 실행

**PowerShell 창 1 (app.py):**
```powershell
streamlit run app.py --server.port 8501
```

**PowerShell 창 2 (test.py):**
```powershell
streamlit run test.py --server.port 8502
```

### 접속 주소
- **로컬**:
  - app.py (DB 모니터링): http://localhost:8501
  - test.py (Oracle 분석): http://localhost:8502
- **Streamlit Cloud**:
  - https://lgusdofwsukagfatwzhn3f.streamlit.app/

## Supabase 연결 정보

### 필요한 정보
- **Project URL**: https://[PROJECT_ID].supabase.co
- **API Key**: Settings → API → anon public key

### 데이터 테이블 구조

#### dba_monitoring 테이블
- **설명**: DB 모니터링 지표 데이터
- **데이터 범위**: 2026-06-01 ~ 2026-06-15 (30분 단위, 2,160행)
- **컬럼 정보**:
  | 컬럼명 | 타입 | 설명 |
  |--------|------|------|
  | `id` | int8 | 자동 증가 ID (Primary Key) |
  | `timestamp` | timestamp | 데이터 수집 시간 |
  | `db_name` | varchar | 데이터베이스명 (PROD_DB, DEV_DB, TEST_DB) |
  | `cpu_usage` | int4 | CPU 사용률 (%) |
  | `active_sessions` | int4 | Active Session 수 |
  | `lock_sessions` | int4 | Lock Session 수 |
  | `alertlog_count` | int4 | Alert 로그 개수 |
  | `created_at` | timestamp | 레코드 생성 시간 |

#### hnsmall_broadcast 테이블 (신규)
- **설명**: 홈앤쇼핑 TV 편성표 데이터
- **데이터 범위**: 2026-06-01 ~ 2026-06-15 (1시간 단위, 360행)
- **용도**: DB 모니터링 대시보드의 방송 정보 표시
- **컬럼 정보**:
  | 컬럼명 | 타입 | 설명 |
  |--------|------|------|
  | `id` | int8 | 자동 증가 ID (Primary Key) |
  | `timestamp` | timestamp | 방송 시작 시간 |
  | `end_time` | timestamp | 방송 종료 시간 |
  | `program_name` | varchar | 프로그램명 (상품명 + "특가 방송") |
  | `product_name` | varchar | 상품명 |
  | `product_price` | varchar | 상품 가격 |
  | `description` | varchar | 상품 설명 |
  | `duration_minutes` | int4 | 방송 시간 (분) |
  | `channel` | varchar | 채널명 (HOME & SHOPPING) |
  | `host` | varchar | 진행자명 |
  | `created_at` | timestamp | 레코드 생성 시간 |

### Streamlit Cloud 배포 설정
- **배포 방식**: GitHub 연동 (main 브랜치 자동 배포)
- **Secrets 관리**: Streamlit Cloud 대시보드 → Settings → Secrets
  ```toml
  supabase_url = "https://[PROJECT_ID].supabase.co"
  supabase_key = "your_anon_public_key"
  anthropic_api_key = "your_anthropic_api_key"
  ```

## 데이터 생성

### DB 모니터링 데이터 생성 (generate_data.py)
```powershell
python generate_data.py
```
- 6월 1일 00:00 ~ 6월 15일 23:30 범위
- 30분 간격으로 2,160개 행 생성
- 3개 DB별 가상 모니터링 데이터 생성
- CSV 파일 생성 및 Supabase에 자동 업로드 시도

### TV 편성표 데이터 생성 (generate_broadcast_data.py)
```powershell
python generate_broadcast_data.py
```
- 6월 1일 00:00 ~ 6월 15일 23:00 범위
- 1시간 단위로 360개 행 생성
- 10개 상품별 방송 정보 생성 (시간 단위로 순환)
- 방송 시작시간 및 종료시간 포함
- CSV 파일 생성: `hnsmall_broadcast_sample.csv`

### Supabase 업로드
```powershell
python upload_broadcast_to_supabase.py
```
- CSV 파일을 Supabase `hnsmall_broadcast` 테이블에 업로드
- 또는 Supabase UI에서 수동 Import 가능

## 개발 노트

### Supabase 데이터 조회
- **페이징 로직**: 1000개씩 반복 쿼리로 모든 데이터 조회
- **쿼리 최적화**: `range(0, 999999)` 사용으로 제한 없이 조회
- **성능**: 2000개 이상의 데이터도 안정적으로 처리

### Claude AI 요약
- **모델**: claude-opus-4-1
- **최대 토큰**: 1200 tokens
- **글자 제한**: 1000자 이내
- **기능**: 
  - 선택된 기간의 DB 성능 데이터 분석
  - 마크다운 형식의 요약 생성
  - 실시간 스트리밍 출력

### 그래프 시각화
- **x축 포맷 동적 변경**:
  - 1일 이내: 시간만 표시 (`HH:MM`)
  - 2일 이상: 시간 표시 + 자정(00:00)에 날짜 표시
- **모든 그래프**: CPU, Session, Lock, Alert 4개
- **상호작용**: 마우스 호버 시 정확한 수치 표시
- **방송 정보 hover** (PROD_DB만):
  - CPU, Session, Lock, Alert 차트에서 호버 시 방송 정보 표시
  - 표시 정보: 프로그램명, 상품명, 가격, 진행자
  - 시간대 범위 매칭: start_time <= 현재시간 < end_time

### 보안
- API key는 `.streamlit/secrets.toml`에 저장하며 `.gitignore`에 추가
- 로컬 개발 시에만 secrets.toml 파일 사용
- 배포(Streamlit Cloud) 시에는 대시보시에서 secrets 관리
- 모든 API key는 환경변수 또는 Streamlit Secrets로 관리

### 포트 설정
- 기본 Streamlit 포트: 8501
- test.py: 명시적으로 8502 포트 지정
- 포트 변경 시: `--server.port` 옵션 사용

### 종료
- PowerShell에서 `Ctrl+C` 입력으로 각 앱 종료

## 최근 개발 이력

### 2026-06-19 업데이트

#### 기존 업데이트 (전반부)
- ✅ Supabase 직접 연결 (CSV에서 변경)
- ✅ 데이터 확장 (6/1~6/15, 2,160개 행)
- ✅ Supabase 페이징 로직 구현
- ✅ Claude AI 요약 기능 추가
- ✅ 조회 가능 기간 표시 (시작~종료)
- ✅ 그래프 x축 자정 날짜 표시
- ✅ Streamlit Cloud 배포 완료
- ✅ Requirements.txt 업데이트 (anthropic, httpx 추가)

#### 신규 업데이트 (후반부) - TV 편성표 기능
- ✅ TV 편성표 데이터 테이블 생성 (`hnsmall_broadcast`)
- ✅ 샘플 데이터 생성 (generate_broadcast_data.py)
  - 360개 행 (6월 1일~15일, 1시간 단위)
  - 시작시간, 종료시간, 방송 정보 포함
- ✅ 차트에 방송 정보 hover 표시 기능
  - CPU, Session, Lock, Alert 4개 차트 모두 적용
  - PROD_DB만 선택했을 때만 표시
- ✅ PROD_DB 필터링
  - 차트: PROD_DB hover에만 방송 정보 표시
  - TV편성표: PROD_DB 선택 시에만 표시
- ✅ 시간대 범위 매칭 (start_time ~ end_time)
  - 30분 단위 모니터링 데이터에 정확한 방송 정보 매칭
  - 예: 13:30 데이터 → 13:00~14:00 방송 정보 표시
- ✅ Supabase 테이블 스키마 확정
  - end_time 컬럼 추가
  - 방송마다 다른 방송 시간 대응 가능
