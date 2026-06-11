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
- **포트**: 8501
- **설명**: 데이터베이스 성능 지표를 실시간으로 모니터링하는 대시보드
- **기능**:
  - CPU 사용률 추이 시각화
  - Active Session 수 모니터링
  - Lock Session 수 추적
  - Alert 로그 개수 분석
  - 날짜/시간 범위 필터링
  - DB별 선택적 모니터링
  - 데이터 CSV 다운로드
- **외부 의존성**: Supabase 데이터베이스 (필수)
- **실행 명령어**:
  ```powershell
  streamlit run app.py --server.port 8501
  ```

## 설치 및 실행

### 필수 패키지 설치
```powershell
pip install streamlit pandas plotly numpy supabase
```

### Supabase 설정 (app.py용)

1. Supabase 프로젝트 생성 (https://supabase.com)
2. CSV 데이터를 Supabase \dba_monitoring\ 테이블에 업로드
3. \.streamlit/secrets.toml\ 파일 생성:
   ```toml
   supabase_url = "https://[PROJECT_ID].supabase.co"
   supabase_key = "your_anon_public_key"
   ```
4. \.gitignore\에 \.streamlit/secrets.toml\ 추가 (API key 보안)

### 동시 실행

**PowerShell 창 1 (app.py):**
```powershell
streamlit run app.py --server.port 8501
```

**PowerShell 창 2 (test.py):**
```powershell
streamlit run test.py --server.port 8502
```

### 접속 주소
- app.py (DB 모니터링): http://localhost:8501
- test.py (Oracle 분석): http://localhost:8502

## Supabase 연결 정보

### 필요한 정보
- **Project URL**: \https://[PROJECT_ID].supabase.co\
- **API Key**: Settings → API → anon public key

### 데이터 테이블 구조
- **테이블명**: \dba_monitoring\
- **필수 컬럼**:
  - \db_name\: 데이터베이스명
  - \cpu_usage\: CPU 사용률 (%)
  - \ctive_sessions\: Active Session 수
  - \lock_sessions\: Lock Session 수
  - \lertlog_count\: Alert 로그 수
  - \	imestamp\: 데이터 수집 시간

## 개발 노트

### 보안
- API key는 \.streamlit/secrets.toml\에 저장하며 \.gitignore\에 추가
- 로컬 개발 시에만 secrets.toml 파일 사용
- 배포(Streamlit Cloud) 시에는 대시보드에서 secrets 관리

### 포트 설정
- 기본 Streamlit 포트는 8501
- test.py는 명시적으로 8502 포트 지정
- 포트 변경 시 \--server.port\ 옵션 사용

### 종료
- PowerShell에서 \Ctrl+C\ 입력으로 각 앱 종료
