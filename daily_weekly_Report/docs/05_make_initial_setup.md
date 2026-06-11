# 페이즈 2-3: Make.com 초기 설정 가이드

Make.com을 사용하여 Google Sheets의 데이터를 Google Docs 템플릿에 자동으로 채우고, Outlook으로 발송하는 워크플로우를 만들기 위한 초기 설정입니다.

## 📋 작업 개요

**목표**: Make.com 계정 생성 및 Google 서비스 연동
**예상 시간**: 10분
**필수 요구사항**: Google 계정

---

## 📊 데이터 흐름 (전체 개요)

```
Google Forms
    ↓ (자동 저장)
Google Sheets (일일 업무 데이터)
    ↓ (Make.com이 읽기)
Make.com (자동화 엔진)
    ├→ 데이터 수집
    ├→ 이미지 처리
    ├→ Google Docs 템플릿 복제
    ├→ 데이터 입력
    └→ Outlook 발송
```

---

## 단계별 진행

### Step 1️⃣: Make.com 회원가입

1. https://www.make.com 방문
2. **"Sign up for free"** 또는 **"무료 가입"** 버튼 클릭
3. 이메일 입력: `사용자@gmail.com`
4. 비밀번호 설정
5. **"가입"** 또는 **"Sign up"** 클릭
6. 이메일 인증 완료

**예상 시간**: 2-3분

---

### Step 2️⃣: Make.com 대시보드 확인

가입 후 Make.com 대시보드가 열립니다:

```
┌─────────────────────────────────┐
│  Welcome to Make             ✓  │
├─────────────────────────────────┤
│ "Create a scenario" 또는         │
│ "Create your first automation"  │
└─────────────────────────────────┘
```

**아직 시나리오를 만들지 마세요!**
먼저 Google 계정들을 연동해야 합니다.

---

### Step 3️⃣: Google 계정 연동 - Sheets

#### 3-1: 설정 접속

1. Make.com 좌측 메뉴에서 **"Connections"** 또는 **"설정"** 클릭
2. 또는 우상단 프로필 아이콘 → **"Connections"**

#### 3-2: Google Sheets 연동

1. **"New connection"** 또는 **"새 연결"** 버튼 클릭
2. **"Google"** 검색
3. **"Google Sheets"** 선택
4. **"Connect"** 또는 **"연결"** 클릭
5. Google 로그인 창 열림
6. **사용자의 Google 계정 선택** (forms, sheets를 만들 때 사용한 계정)
7. **"허용"** 또는 **"Allow"** 클릭
8. Make.com으로 돌아감 → 연결 완료 ✅

---

### Step 4️⃣: Google 계정 연동 - Docs

동일한 방법으로 Google Docs 연동:

1. **"New connection"** 클릭
2. **"Google"** 검색
3. **"Google Docs"** 선택 (또는 "Google Drive")
4. **"Connect"** 클릭
5. Google 로그인 (이미 로그인되어 있으면 자동)
6. **"허용"** 클릭
7. 연결 완료 ✅

---

### Step 5️⃣: Google 계정 연동 - Drive (이미지 다운로드용)

1. **"New connection"** 클릭
2. **"Google"** 검색
3. **"Google Drive"** 선택
4. **"Connect"** 클릭
5. 허용 → 연결 완료 ✅

---

### Step 6️⃣: Outlook 계정 연동 (이메일 발송용)

1. **"New connection"** 클릭
2. **"Outlook"** 또는 **"Microsoft"** 검색
3. **"Outlook"** 또는 **"Office 365 Outlook"** 선택
4. **"Connect"** 클릭
5. **Microsoft 계정 로그인** (Outlook 계정)
   - outlook.com 또는 outlook.kr 이메일
   - 또는 Microsoft 365 계정
6. **"수락"** 또는 **"Accept"** 클릭
7. Make.com으로 돌아감 → 연결 완료 ✅

---

### Step 7️⃣: 연동 확인

Connections 페이지에서 다음이 모두 표시되어야 합니다:

```
✅ Google Sheets
✅ Google Docs (또는 Google Drive)
✅ Google Drive
✅ Outlook (또는 Office 365 Outlook)
```

---

## 📌 저장할 정보

### make_setup.txt 파일 생성

**경로**: `c:\git_test\edu\daily_weekly_Report\docs\make_setup.txt`

**내용**:
```
Make.com 초기 설정 완료

계정 정보:
- Make.com 계정: [사용자 이메일]
- 가입 날짜: 2026-06-11

연동된 서비스:
✅ Google Sheets
✅ Google Docs
✅ Google Drive
✅ Outlook

플랜: Free (무료 플랜)
- 월 1000개 operation 포함

다음 단계:
페이즈 3 - Make.com 워크플로우 구성
```

---

## ⚠️ 주의사항

### Free 플랜 한계

Make.com의 무료 플랜:
- ✅ 월 1000개 operation (충분함)
- ✅ 기본 기능 모두 사용 가능
- ❌ 고급 기능 (AI 도구 등) 제한

현재 프로젝트는 무료 플랜으로 충분합니다!

### 보안

- **API 키 저장 금지**: Make.com이 안전하게 관리함
- **연결 공개 금지**: 개인/개인 연결 권장
- **테스트 후 활성화**: 전체 워크플로우 테스트 후 스케줄 활성화

---

## ✅ 완료 기준

- [ ] Make.com 계정 생성됨
- [ ] Google Sheets 연동 완료
- [ ] Google Docs 연동 완료
- [ ] Google Drive 연동 완료
- [ ] Outlook 연동 완료
- [ ] 모든 연결이 Connections 페이지에 표시됨
- [ ] make_setup.txt에 정보 저장됨

---

## 💡 팁

### 계정 선택 실패 시

Google 로그인 창에서 계정이 안 보이면:
1. "계정 추가" 또는 "Add account" 클릭
2. 사용자의 Google 이메일 입력
3. 비밀번호 입력
4. 허용

### 연결 테스트

Make.com의 각 연결을 테스트해보려면:
1. Connections 페이지에서 연결 클릭
2. "Test connection" 또는 "연결 테스트" 클릭
3. 성공하면 "Connection test successful" 표시

---

## 🚨 문제 해결

### Q: Google 계정이 여러 개인데, 어느 것을 선택해야 하나?

A: **Google Forms와 Google Sheets를 만들 때 사용한 계정**을 선택하세요.

확인 방법:
1. Google Drive 방문 (https://drive.google.com)
2. 좌상단에 표시된 계정 확인
3. 그 계정의 이메일 주소 기억
4. Make.com에서 동일한 계정 선택

---

### Q: Outlook 계정이 없는데?

A: 두 가지 방법:
1. **Outlook.com 가입** (무료): https://outlook.com
   - 이메일 주소: yourname@outlook.com
   - 가입 후 Make.com에 연동

2. **Gmail 사용** (Make.com에서 Gmail 지원):
   - 대신 Gmail 계정을 연동
   - 이메일 발송은 Gmail로 진행

---

### Q: 연결이 실패했다고 나와요

A: 확인할 사항:
1. 인터넷 연결 확인
2. 팝업 차단 확인 (Google 로그인 팝업이 나타나야 함)
3. 2단계 인증 확인 (필요하면 앱 비밀번호 사용)
4. Make.com 설정에서 "Reconnect" 또는 "다시 연결" 시도

---

## 다음 단계

페이즈 2-3 완료 후 이동:
👉 **페이즈 3**: Make.com 워크플로우 구성
   → 매주 금요일 10:00에 자동으로 보고서 생성 및 이메일 발송
