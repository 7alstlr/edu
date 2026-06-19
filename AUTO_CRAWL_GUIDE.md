# 🤖 자동 크롤링 가이드

로컬 컴퓨터에서 주기적으로 홈쇼핑 편성표를 크롤링하고 자동으로 Supabase에 업로드합니다.

## 설치

### 1. 필수 패키지 설치
```powershell
pip install -r requirements.txt
```

또는 직접 설치:
```powershell
pip install schedule requests beautifulsoup4 pandas supabase
```

## 사용법

### 옵션 1: 수동 실행 (한 번만)

```powershell
python auto_crawl_broadcast.py
```

**작동:**
1. 홈쇼핑모아에서 현재 방송 정보 크롤링
2. `broadcast_data.csv` 파일 생성
3. Supabase `hnsmall_broadcast` 테이블에 업로드
4. 로그: `broadcast_crawl.log`에 저장

### 옵션 2: 자동 스케줄 (주기적 실행)

**6시간마다 실행:**
```powershell
python auto_crawl_broadcast.py --schedule
```

**커스텀 간격 (예: 3시간마다):**
```powershell
python auto_crawl_broadcast.py --schedule 3
```

**실행 중지:**
`Ctrl + C` 입력

## Windows 자동화 설정

### Task Scheduler를 이용한 자동 실행

**1단계: Task Scheduler 열기**
```
Windows 검색 → "작업 스케줄러" 실행
```

**2단계: 새 작업 만들기**
- 작업 스케줄러 라이브러리 → "작업 만들기"
- 일반 탭:
  - 이름: `홈쇼핑 편성표 크롤링`
  - "가장 높은 권한으로 실행" 체크

**3단계: 트리거 설정**
- 트리거 탭 → "새로 만들기"
- 설정:
  - 시작: 매일 자정(00:00)
  - 반복: 6시간마다
  - 활성화: ✓

**4단계: 작업 설정**
- 작업 탭 → "새로 만들기"
- 프로그램: `C:\Python\python.exe` (Python 경로)
- 인수: `c:\claude_test\edu\auto_crawl_broadcast.py`
- 시작 위치: `c:\claude_test\edu`

**5단계: 조건 설정** (선택사항)
- 조건 탭:
  - "전원 설정" → "컴퓨터가 AC에 연결되어 있을 때만 실행" 체크
  - "네트워크" → "모든 네트워크 연결이 사용 가능할 때만 실행" 체크

**6단계: 저장**
- 확인 → 작업 생성

### PowerShell로 자동화

```powershell
# 매일 자정에 실행되는 스케줄 작업 생성
$action = New-ScheduledTaskAction -Execute "C:\Python\python.exe" `
  -Argument "c:\claude_test\edu\auto_crawl_broadcast.py" `
  -WorkingDirectory "c:\claude_test\edu"

$trigger = New-ScheduledTaskTrigger -Daily -At 00:00

Register-ScheduledTask -TaskName "홈쇼핑 편성표 크롤링" `
  -Action $action -Trigger $trigger -RunLevel Highest
```

## 로그 확인

크롤링 작업의 상태는 `broadcast_crawl.log`에서 확인:

```powershell
# 로그 파일 실시간 모니터링
Get-Content broadcast_crawl.log -Wait
```

**로그 예시:**
```
2026-06-20 09:00:00,000 - INFO - ============================================================
2026-06-20 09:00:00,001 - INFO - 🎬 자동 크롤링 작업 시작 - 2026-06-20 09:00:00.000123
2026-06-20 09:00:00,100 - INFO - [1/3] 홈쇼핑모아 편성표 크롤링 시작...
2026-06-20 09:00:01,200 - INFO - ✅ 페이지 접근 성공 (상태: 200)
2026-06-20 09:00:02,300 - INFO - [2/3] 편성표 데이터 추출 중...
2026-06-20 09:00:02,400 - INFO - 📊 5개 방송 항목 추출됨
2026-06-20 09:00:02,500 - INFO - [3/3] CSV 파일 저장 중...
2026-06-20 09:00:02,600 - INFO - ✅ CSV 저장 완료: broadcast_data.csv
2026-06-20 09:00:03,700 - INFO - Supabase에 데이터 업로드 중...
2026-06-20 09:00:04,800 - INFO - ✅ 총 5행 업로드 완료
```

## 문제 해결

### 크롤링이 안 될 때

1. **홈쇼핑모아 HTML 구조 변경**
   - `auto_crawl_broadcast.py`의 CSS 선택자 수정 필요
   - 개발자 도구(F12)에서 실제 HTML 구조 확인

2. **IP 차단**
   - User-Agent 변경
   - 요청 간격 늘리기 (time.sleep() 추가)

3. **Supabase 연결 오류**
   - API 키 확인 (SUPABASE_URL, SUPABASE_KEY)
   - 테이블 이름 확인 (`hnsmall_broadcast`)

### Task Scheduler 실행 안 될 때

```powershell
# Task Scheduler 작업 삭제
Unregister-ScheduledTask -TaskName "홈쇼핑 편성표 크롤링" -Confirm:$false

# 로그 확인
Get-ScheduledTaskInfo -TaskName "홈쇼핑 편성표 크롤링"
```

## 파일 설명

| 파일 | 설명 |
|------|------|
| `auto_crawl_broadcast.py` | 메인 크롤링 스크립트 |
| `broadcast_data.csv` | 생성된 방송 데이터 (수동 실행 시) |
| `broadcast_crawl.log` | 실행 로그 (추적용) |

## 주의사항

⚠️ **법적 고려사항**
- 홈쇼핑모아의 이용약관 확인 필수
- 개인 학습/프로젝트용으로만 사용
- 상업적 이용은 공식 API 이용 권장

⚠️ **기술적 주의**
- 과도한 크롤링은 서버에 부담
- 에러 처리 있음 (샘플 데이터로 폴백)
- 크롤링 실패해도 작업 중단되지 않음

## 향후 개선

- [ ] 실제 홈쇼핑모아 HTML 구조 맞춤 (크롤링 성공률 향상)
- [ ] 프록시 로테이션 (IP 차단 대응)
- [ ] 이메일 알림 (성공/실패)
- [ ] 데이터베이스 동기화 확인
- [ ] 에러 복구 자동화

---

**문제가 있거나 개선 사항이 있으면 알려주세요!** 🚀
