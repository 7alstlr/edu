# 아키텍처 & 기술 설정

이 문서는 프로젝트의 기술 아키텍처, 설정 정보, 데이터 구조를 정의합니다.

## 애플리케이션 정보

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

### 2. app.py - DB 모니터링 대시보드
- **포트**: 8501 (로컬) / Streamlit Cloud (배포)
- **설명**: 데이터베이스 성능 지표와 TV 편성표를 실시간으로 모니터링
- **주요 기능**:
  - 4개 그래프: CPU, Active Session, Lock Session, Alert 로그
  - 날짜/시간 범위 필터링
  - DB별 선택적 모니터링
  - Claude AI 자동 요약 (1000자 이내)
  - 📺 홈앤쇼핑 TV 편성표 (PROD_DB 선택 시)
    - 차트 hover 시 방송 정보 표시
    - 시간대 범위 매칭 (start_time ~ end_time)
- **외부 의존성**: Supabase (필수), Anthropic Claude API (선택)

## Supabase 설정

### 필요한 정보
- **Project URL**: https://[PROJECT_ID].supabase.co
- **API Key**: Settings → API → anon public key
- **RLS 설정**: Disabled (데이터 접근 제한 해제)

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

#### hnsmall_broadcast 테이블
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

## 기술 정보

### 포트 설정
- app.py: 8501 (기본)
- test.py: 8502 (명시적 지정)
- 변경 시: `streamlit run [file].py --server.port [PORT]`

### Supabase 데이터 조회
- **페이징 로직**: 1000개씩 반복 쿼리로 모든 데이터 조회
- **쿼리 최적화**: `range(0, 999999)` 사용으로 제한 없이 조회
- **성능**: 2000개 이상의 데이터도 안정적으로 처리

### Claude AI 요약
- **모델**: claude-opus-4-1
- **최대 토큰**: 1200 tokens
- **글자 제한**: 1000자 이내
- **기능**: 선택된 기간의 DB 성능 데이터 분석 및 마크다운 형식 요약

### 그래프 시각화
- **x축 포맷 동적 변경**:
  - 1일 이내: 시간만 표시 (`HH:MM`)
  - 2일 이상: 시간 표시 + 자정(00:00)에 날짜 표시
- **모든 그래프**: CPU, Session, Lock, Alert 4개
- **상호작용**: 마우스 호버 시 정확한 수치 표시
- **방송 정보 hover** (PROD_DB만):
  - CPU, Session, Lock, Alert 차트에서 hover 시 방송 정보 표시
  - 시간대 범위 매칭: `timestamp <= 현재시간 < end_time`

### 보안
- API key는 `.streamlit/secrets.toml`에 저장하며 `.gitignore`에 추가
- 로컬 개발 시에만 secrets.toml 파일 사용
- 배포(Streamlit Cloud) 시에는 대시보드에서 secrets 관리
- 모든 API key는 환경변수 또는 Streamlit Secrets로 관리

### 패키지 요구사항
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.0.0
numpy>=1.20.0
supabase>=2.0.0
anthropic>=0.7.0
httpx>=0.24.0
python-dotenv>=1.0.0
```

## 주요 파일 설명

| 파일명 | 설명 |
|--------|------|
| `app.py` | DB 모니터링 대시보드 메인 파일 |
| `test.py` | Oracle Alert Log 분석기 |
| `generate_data.py` | DB 모니터링 가상 데이터 생성 |
| `generate_broadcast_data.py` | TV 편성표 가상 데이터 생성 |
| `upload_broadcast_to_supabase.py` | 편성표 데이터 Supabase 업로드 |
| `.streamlit/secrets.toml` | API 키 및 환경 설정 (gitignore) |
| `requirements.txt` | Python 패키지 의존성 |

---

**관련 문서:**
- [README.md](README.md) - 프로젝트 소개 및 빠른시작
- [CHANGELOG.md](CHANGELOG.md) - 개발 이력 및 기술 결정사항
