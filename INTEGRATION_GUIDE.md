# Supabase & Streamlit Cloud 통합 가이드

이 문서는 CSV 파일을 Supabase로 마이그레이션하고, Streamlit 앱과 연동하는 전체 과정을 기록합니다.

---

## 📋 목차

1. [Phase 1: CSV → Supabase 마이그레이션](#phase-1-csv--supabase-마이그레이션)
2. [Phase 2: Streamlit 앱 연동](#phase-2-streamlit-앱-연동)
3. [Phase 3: GitHub 업로드](#phase-3-github-업로드)
4. [Phase 4: Streamlit Cloud 배포](#phase-4-streamlit-cloud-배포)
5. [완료 체크리스트](#완료-체크리스트)

---

## Phase 1: CSV → Supabase 마이그레이션

### 1.1 CSV 파일 준비

**파일:** `C:\kms\dba_monitoring.csv`

**데이터 구조:**
```
timestamp,DB명,CPU사용율(%),Active Session 수,Lock Session 수,AlertLog Count
2026-06-02 08:00:00,PROD_DB,49,207,8,22
2026-06-02 08:00:00,DEV_DB,22,44,0,0
...
```

**데이터 통계:**
- 총 384개 행
- 3개 데이터베이스: PROD_DB, DEV_DB, TEST_DB
- 시간범위: 2026-06-02 ~ 2026-06-04

### 1.2 Supabase 테이블 생성

**테이블명:** `dba_monitoring`

**SQL 스크립트:**
```sql
CREATE TABLE dba_monitoring (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  timestamp TIMESTAMP NOT NULL,
  db_name VARCHAR(50) NOT NULL,
  cpu_usage INTEGER NOT NULL,
  active_sessions INTEGER NOT NULL,
  lock_sessions INTEGER NOT NULL,
  alertlog_count INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dba_monitoring_timestamp ON dba_monitoring(timestamp);
CREATE INDEX idx_dba_monitoring_db_name ON dba_monitoring(db_name);
```

**실행 방법:**
```bash
# Supabase MCP 도구로 실행
mcp__supabase__execute_sql 사용
```

### 1.3 CSV 데이터 삽입

**Python 스크립트로 데이터 정규화:**
```python
import csv
import json

# CSV 읽기 (UTF-8 BOM 처리)
with open('dba_monitoring.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    data = list(reader)

# 컬럼명 매핑
normalized_data = []
for row in data:
    normalized_row = {
        'timestamp': row['timestamp'],
        'db_name': row['DB명'],
        'cpu_usage': int(row['CPU사용율(%)']),
        'active_sessions': int(row['Active Session 수']),
        'lock_sessions': int(row['Lock Session 수']),
        'alertlog_count': int(row['AlertLog Count'])
    }
    normalized_data.append(normalized_row)
```

**데이터 삽입:**
```sql
INSERT INTO dba_monitoring (timestamp, db_name, cpu_usage, active_sessions, lock_sessions, alertlog_count)
VALUES 
  ('2026-06-02 08:00:00', 'PROD_DB', 49, 207, 8, 22),
  ('2026-06-02 08:00:00', 'DEV_DB', 22, 44, 0, 0),
  ...
  -- 총 384개 행
```

**검증:**
```sql
SELECT COUNT(*) as total, MIN(timestamp) as earliest, MAX(timestamp) as latest 
FROM dba_monitoring;
-- 결과: total=384, earliest=2026-06-02 08:00:00, latest=2026-06-04 23:30:00
```

---

## Phase 2: Streamlit 앱 연동

### 2.1 Supabase 연결 정보 확보

**필요한 정보:**
| 항목 | 값 |
|------|-----|
| Project URL | https://qllwpvkzsybjlhhuvbto.supabase.co |
| Anon Key | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |

**획득 방법:**
1. Supabase 대시보드 접속
2. Settings > API
3. Project URL, anon (public) key 복사

### 2.2 app.py 수정

**변경 전 (CSV 읽기):**
```python
@st.cache_data
def load_data():
    df = pd.read_csv('dba_monitoring.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df
```

**변경 후 (Supabase 읽기):**
```python
from supabase import create_client

@st.cache_data
def load_data():
    try:
        supabase_url = st.secrets["supabase_url"]
        supabase_key = st.secrets["supabase_key"]
        
        supabase = create_client(supabase_url, supabase_key)
        response = supabase.table("dba_monitoring").select("*").execute()
        
        df = pd.DataFrame(response.data)
        
        # 컬럼명 매핑 (Supabase → CSV 형식)
        df.rename(columns={
            'db_name': 'DB명',
            'cpu_usage': 'CPU사용율(%)',
            'active_sessions': 'Active Session 수',
            'lock_sessions': 'Lock Session 수',
            'alertlog_count': 'AlertLog Count'
        }, inplace=True)
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
        
    except KeyError:
        st.error("Streamlit Secrets에 supabase_url, supabase_key 필요")
        return pd.DataFrame()
```

**수정 파일:**
- `app.py` (원본)
- `app_modified.py` (수정본)

### 2.3 패키지 업데이트

**requirements.txt 추가:**
```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.0.0
supabase>=2.0.0
python-dotenv>=1.0.0
```

### 2.4 로컬 환경변수 설정

**파일:** `.env`
```bash
SUPABASE_URL=https://qllwpvkzsybjlhhuvbto.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**파일:** `.streamlit/secrets.toml`
```toml
supabase_url = "https://qllwpvkzsybjlhhuvbto.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**주의:** `.gitignore`에 다음 추가
```
.env
.streamlit/secrets.toml
```

---

## Phase 3: GitHub 업로드

### 3.1 커밋 이력

**Commit 1: Supabase 초기 설정**
```bash
git add requirements.txt test.py SETUP.md .env.example
git commit -m "Add Supabase integration and DBA monitoring dashboard"
git push origin main
```
- **Commit Hash:** ce66e3b

**Commit 2: app.py Supabase 연동**
```bash
git add app.py
git commit -m "feat: Supabase 연동 - CSV 대신 Supabase 테이블에서 데이터 읽기"
git push origin main
```
- **Commit Hash:** d1797d9

**Commit 3: Streamlit 설정 추가**
```bash
git add .streamlit/secrets.toml.example
git commit -m "Add Streamlit secrets configuration template"
git push origin main
```
- **Commit Hash:** bf246f3

### 3.2 GitHub 저장소 구조

```
edu/
├── app.py                          # Supabase 연동 버전
├── requirements.txt                # 패키지 의존성
├── .gitignore                      # Git 제외 설정
├── .env.example                    # 환경변수 템플릿
├── SETUP.md                        # 설정 가이드
├── INTEGRATION_GUIDE.md            # 이 문서
├── .streamlit/
│   └── secrets.toml.example        # Streamlit 설정 템플릿
├── dba_monitoring.csv              # 원본 데이터
└── ...
```

---

## Phase 4: Streamlit Cloud 배포

### 4.1 Streamlit Cloud 설정

**URL:** https://lgusdofwsukagfatwzhn3f.streamlit.app/

**Secrets 설정 단계:**

1. Streamlit Cloud 대시보드 접속
   - https://share.streamlit.io/

2. 앱 선택 후 ⚙️ **Settings** 클릭

3. **Secrets** 탭 클릭

4. 다음 내용 추가:
```toml
supabase_url = "https://qllwpvkzsybjlhhuvbto.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsbHdwdmt6c3liamxoaHV2YnRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1NTQ4NzgsImV4cCI6MjA5NjEzMDg3OH0.4HfZQc6O72dYuOwNTs0mvCeNmkQfYE7Bfht7aX0kfMM"
```

5. **Save** 클릭

**자동 배포:**
- Streamlit Cloud이 GitHub 변경사항을 감지하면 자동으로 재배포됩니다.

### 4.2 배포 확인

**체크사항:**
```
✅ 앱이 정상 로드되는가?
✅ Supabase에서 데이터를 읽는가?
✅ 차트와 테이블이 표시되는가?
✅ 메트릭 카드가 업데이트되는가?
```

**URL:** https://lgusdofwsukagfatwzhn3f.streamlit.app/

---

## 완료 체크리스트

### 데이터 마이그레이션
- [x] CSV 파일 읽기
- [x] Supabase 테이블 생성
- [x] 데이터 정규화 및 삽입 (384개 행)
- [x] 데이터 검증

### 코드 수정
- [x] app.py Supabase 연동
- [x] 컬럼명 매핑 (Supabase → CSV 형식)
- [x] 에러 처리 추가
- [x] 캐싱 설정

### 환경 설정
- [x] `.env` 파일 생성
- [x] `.streamlit/secrets.toml` 생성
- [x] requirements.txt 업데이트
- [x] .gitignore 설정

### GitHub 업로드
- [x] 3개 커밋 완료
- [x] 모든 파일 푸시
- [x] 저장소 구조 확인

### Streamlit Cloud 배포
- [x] Secrets 설정
- [x] 자동 배포 확인
- [x] 앱 정상 작동 확인

---

## 🔑 주요 정보

### Supabase 프로젝트
- **Project URL:** https://qllwpvkzsybjlhhuvbto.supabase.co
- **Table:** dba_monitoring (384 rows)
- **Primary Key:** id (auto-increment)

### GitHub 저장소
- **URL:** https://github.com/7alstlr/edu
- **Branch:** main
- **Last Commit:** bf246f3

### Streamlit Cloud 앱
- **URL:** https://lgusdofwsukagfatwzhn3f.streamlit.app/
- **Status:** Active
- **Data Source:** Supabase (dba_monitoring table)

---

## 🚀 다음 단계

### 로컬 테스트 방법
```bash
# 1. 저장소 클론
git clone https://github.com/7alstlr/edu.git
cd edu

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 설정
# .streamlit/secrets.toml 파일 생성 후 값 입력

# 4. 앱 실행
streamlit run app.py
```

### 데이터 업데이트 방법
```bash
# CSV 파일 업데이트 후
python -c "
import pandas as pd
from supabase import create_client

df = pd.read_csv('dba_monitoring.csv')
# 정규화 및 Supabase 업로드
"
```

### 트러블슈팅

**문제:** Supabase 연결 오류
```
해결:
1. Supabase 프로젝트 활성화 확인
2. API 키 정확성 확인
3. .streamlit/secrets.toml 권한 확인
```

**문제:** 데이터가 표시되지 않음
```
해결:
1. Supabase 테이블 데이터 확인
2. 컬럼명 매핑 확인
3. 캐시 초기화 (Ctrl+R)
```

**문제:** GitHub 푸시 실패
```
해결:
1. git pull origin main
2. 충돌 해결
3. git push origin main 재시도
```

---

## 📚 참고 자료

- [Supabase 문서](https://supabase.com/docs)
- [Streamlit 문서](https://docs.streamlit.io)
- [Streamlit Cloud 배포](https://docs.streamlit.io/streamlit-cloud)
- [Python CSV 처리](https://docs.python.org/3/library/csv.html)

---

## 📝 작성일

**작성:** 2026-06-04
**작성자:** Claude
**버전:** 1.0

---

## 🔄 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 1.0 | 2026-06-04 | 초기 문서 작성 |

