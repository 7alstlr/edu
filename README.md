# 📊 DB 모니터링 대시보드 & 📺 홈앤쇼핑 TV 편성표

두 개의 Streamlit 대시보드 애플리케이션으로 구성된 통합 모니터링 시스템입니다.

## 🎯 주요 기능

### 1. DB 모니터링 대시보드 (app.py)
- **CPU 사용률** 추이 시각화
- **Active Session 수** 모니터링
- **Lock Session 수** 추적
- **Alert 로그 개수** 분석
- 날짜/시간 범위 필터링
- DB별 선택적 모니터링 (PROD_DB, DEV_DB, TEST_DB)
- **📺 TV 편성표** (PROD_DB와 동시 조회)
  - 차트 hover 시 실시간 방송 정보 표시
  - 프로그램, 상품, 가격, 진행자 정보 포함
  - 정확한 시간대 범위 매칭
- Claude AI를 이용한 자동 요약 (1000자 이내)
- 데이터 CSV 다운로드

### 2. Oracle Alert Log 분석기 (test.py)
- Alert Log 텍스트 입력으로 Oracle 에러 코드 자동 추출
- 에러 코드별 상세 정보 제공 (원인, 조치 방법)
- 크리티컬 에러 강조 표시
- 에러 코드 검색 및 필터링

## 🚀 빠른 시작

### 필수 요구사항
- Python 3.8+
- Streamlit
- Supabase 계정

### 설치

```bash
# 패키지 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install streamlit pandas plotly numpy supabase anthropic httpx python-dotenv
```

### 실행

**PowerShell 창 1 - DB 모니터링 대시보드:**
```powershell
streamlit run app.py --server.port 8501
```

**PowerShell 창 2 - Oracle 분석기:**
```powershell
streamlit run test.py --server.port 8502
```

### 접속 주소
- **로컬 - DB 모니터링**: http://localhost:8501
- **로컬 - Oracle 분석**: http://localhost:8502
- **Streamlit Cloud**: https://lgusdofwsukagfatwzhn3f.streamlit.app/

## 📋 데이터 준비

### Supabase 설정

1. [Supabase](https://supabase.com)에서 프로젝트 생성
2. `.streamlit/secrets.toml` 파일 생성:
   ```toml
   supabase_url = "https://[PROJECT_ID].supabase.co"
   supabase_key = "your_anon_public_key"
   anthropic_api_key = "your_anthropic_api_key"
   ```
3. `.gitignore`에 `.streamlit/secrets.toml` 추가

### 가상 데이터 생성

```bash
# DB 모니터링 데이터 생성
python generate_data.py

# TV 편성표 데이터 생성
python generate_broadcast_data.py

# Supabase에 업로드
python upload_broadcast_to_supabase.py
```

## 📊 데이터 범위

- **모니터링 데이터**: 2026-06-01 ~ 2026-06-15 (30분 단위, 2,160행)
- **방송 편성표**: 2026-06-01 ~ 2026-06-15 (1시간 단위, 360행)

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Backend**: Supabase (PostgreSQL)
- **AI Summary**: Anthropic Claude API
- **Data Processing**: Pandas, NumPy

## 📚 기술 아키텍처

더 자세한 아키텍처 및 설정 정보는 [ARCHITECTURE.md](ARCHITECTURE.md)를 참고해주세요.

## 📝 변경 이력

프로젝트의 개발 이력 및 기술 결정사항은 [CHANGELOG.md](CHANGELOG.md)를 참고해주세요.

## ⚙️ 주요 특징

### 실시간 데이터 연동
- Supabase REST API를 통한 직접 연결
- 페이징 처리로 대용량 데이터 안정적 처리

### 스마트 시간대 매칭
- 방송 정보를 시간 범위로 정확히 매칭
- 30분 단위 모니터링 데이터도 정확한 방송 정보 표시

### 유연한 필터링
- DB별 선택적 모니터링
- 날짜/시간 범위 지정 가능
- PROD_DB 선택 시에만 TV 편성표 표시

### 자동화된 요약
- Claude AI를 이용한 성능 데이터 분석
- 마크다운 형식의 자동 요약
- 1000자 이내로 요약

## 🔒 보안

- API key는 `.streamlit/secrets.toml`에 저장
- `.gitignore`에 secrets 파일 추가
- Streamlit Cloud 배포 시 대시보드에서 별도 관리

## 📞 문의

이슈나 기능 요청은 프로젝트 대시보드에서 해주세요.
