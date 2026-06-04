# DBA 모니터링 & Alert Log 분석기 설정 가이드

## 필수 환경변수 설정

### 1. Supabase 연결 정보 확인

Supabase 대시보드에서 다음 정보를 획득하세요:
- **Project URL**: Settings > API > Project URL
- **Anon Key**: Settings > API > anon (public) key

### 2. .env 파일 생성

프로젝트 루트 디렉토리에 `.env` 파일을 생성하세요:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

### Streamlit 앱 실행

```bash
streamlit run test.py
```

앱이 자동으로 브라우저에서 열립니다. 기본 URL: `http://localhost:8501`

## 주요 기능

### 📊 DBA 모니터링 탭
- **최신 모니터링 데이터**: 각 데이터베이스의 최신 CPU, 활성 세션 정보
- **시계열 차트**: CPU 사용율, 활성 세션, 락 세션, 알림로그 추이 시각화
- **통계 분석**: 데이터베이스별 최소/최대/평균값
- **상세 데이터**: 전체 모니터링 데이터 테이블

### 🔍 Alert Log 분석 탭
- **에러 검색**: ORA- 에러 코드 또는 에러명으로 검색
- **Alert Log 분석**: 입력한 Alert Log에서 ORA- 에러 추출
- **상세 정보**: 각 에러의 원인, 조치 방법 (영어/한국어)
- **크리티컬 에러 알림**: 심각한 에러 강조 표시
- **공식 문서 링크**: Oracle 공식 문서로 바로 이동

## 데이터베이스 테이블 정보

### dba_monitoring 테이블
- `id`: 자동 증가 ID
- `timestamp`: 모니터링 시간 (TIMESTAMP)
- `db_name`: 데이터베이스명 (VARCHAR)
- `cpu_usage`: CPU 사용율 (%) (INTEGER)
- `active_sessions`: 활성 세션 수 (INTEGER)
- `lock_sessions`: 락 세션 수 (INTEGER)
- `alertlog_count`: 알림로그 개수 (INTEGER)
- `created_at`: 생성 시간 (TIMESTAMP)

## 트러블슈팅

### Supabase 연결 오류
- `.env` 파일이 프로젝트 루트에 있는지 확인
- `SUPABASE_URL`과 `SUPABASE_KEY`가 정확한지 확인
- Supabase 프로젝트가 활성화되어 있는지 확인

### 데이터 조회 오류
- Supabase 권한 확인 (RLS 정책)
- 테이블 `dba_monitoring`이 존재하는지 확인

### 패키지 설치 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 환경변수 설정 방법 (Streamlit)

Streamlit에서 공식 권장하는 방법은 `.streamlit/secrets.toml` 사용입니다:

### 방법 1: .streamlit/secrets.toml 파일 생성
```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

### 방법 2: 환경변수 (현재 방식)
```bash
# Windows CMD
set SUPABASE_URL=https://your-project.supabase.co
set SUPABASE_KEY=your-anon-key

# PowerShell
$env:SUPABASE_URL="https://your-project.supabase.co"
$env:SUPABASE_KEY="your-anon-key"

# Linux/Mac
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

## 보안 주의사항

⚠️ **주의**: `.env` 파일을 버전 관리 시스템에 커밋하지 마세요!

`.gitignore`에 다음을 추가하세요:
```
.env
.env.local
.env.*.local
.streamlit/secrets.toml
```

## 개발 서버 시작

```bash
# 자동 리로드 활성화
streamlit run test.py --logger.level=debug
```

## 포트 변경

기본 포트: 8501

```bash
streamlit run test.py --server.port 8000
```
