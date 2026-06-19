# 변경 이력 & 기술 결정사항

프로젝트의 개발 이력, 기술 결정, 구현 세부사항을 기록합니다.

## 개발 노트

### Supabase 데이터 조회 전략

**결정사항**: REST API의 page range 제한(1000행)을 극복하기 위해 페이징 로직 구현

**구현**:
```python
page_size = 1000
offset = 0
while True:
    response = supabase.table(table_name).select('*').range(offset, offset + page_size - 1).execute()
    if not response.data:
        break
    all_data.extend(response.data)
    if len(response.data) < page_size:
        break
    offset += page_size
```

**장점**:
- 2,000행 이상의 대용량 데이터도 안정적으로 처리
- 네트워크 부하 분산

---

### Claude AI 요약 기능

**모델 선택**: claude-opus-4-1
- 이유: 복잡한 데이터 분석과 마크다운 형식 요약에 최적화

**제약사항**:
- 최대 토큰: 1200 tokens
- 최대 글자: 1000자 이내
- 선택된 기간의 DB 성능 데이터 기반 요약

**구현**:
- Streamlit의 `st.write_stream()`을 이용한 실시간 스트리밍 출력
- 마크다운 형식 자동 변환

---

### 그래프 x축 동적 포맷

**문제**: 데이터 범위에 따라 x축 레이블이 너무 많거나 부족함

**해결책**: 조회 기간에 따라 동적으로 포맷 변경
```python
# 1일 이내: 시간만 표시
date_range_days = (filtered_df['timestamp'].max() - filtered_df['timestamp'].min()).days
if date_range_days <= 1:
    xaxis_format = '%H:%M'
else:
    xaxis_format = '%m/%d %H:%M'
```

**추가 기능**: 자정(00:00)에만 날짜 표시
- `add_midnight_labels()` 함수로 자정 지점에 날짜 annotation 추가
- 가독성 향상

---

### TV 편성표 기능 (신규)

#### 1. 데이터 구조 설계

**초기 설계**: 1시간 고정 방송 시간 (`timestamp` + 60분)
```python
duration_minutes = 60
```

**문제점**:
- 실제 방송은 시간이 다양함 (30분, 45분, 90분 등)
- 정시에 시작하지 않을 수 있음

**최종 설계**: `start_time`과 `end_time` 명시적 저장
```python
timestamp: 2026-06-01 13:00:00  # 시작시간
end_time: 2026-06-01 14:00:00   # 종료시간
```

---

#### 2. 차트 Hover 방송 정보 표시

**구현**:
- Plotly의 `customdata`와 `hovertemplate` 활용
- 각 데이터 포인트에 방송 정보 포함

```python
fig.add_trace(go.Scatter(
    x=db_data['timestamp'],
    y=db_data['CPU사용율(%)'],
    customdata=db_data['broadcast_info'],
    hovertemplate='<b>%{fullData.name}</b><br>CPU: %{y:.1f}%<br><br>%{customdata}<extra></extra>'
))
```

**장점**:
- 모니터링 데이터와 방송 정보를 동시에 조회 가능
- 추가 클릭 없이 즉각적인 정보 제공

---

#### 3. 시간대 범위 매칭 알고리즘

**문제**:
- 모니터링 데이터: 30분 단위 (13:00, 13:30, 14:00, ...)
- 방송 데이터: 1시간 단위 (13:00~14:00, 14:00~15:00, ...)
- 정확한 매칭 필요

**해결책**: 시작시간 <= 현재시간 < 종료시간
```python
def get_broadcast_info(timestamp, broadcast_df):
    ts = pd.Timestamp(timestamp)
    broadcast_check = broadcast_df.copy()
    
    # end_time 계산 (duration_minutes 기반)
    if 'end_time' not in broadcast_check.columns:
        broadcast_check['end_time'] = broadcast_check['timestamp'] + \
            pd.to_timedelta(broadcast_check['duration_minutes'], unit='m')
    
    # 범위 매칭
    matching = broadcast_check[
        (broadcast_check['timestamp'] <= ts) &
        (broadcast_check['end_time'] > ts)
    ]
    
    return matching
```

**결과**:
- 13:30 데이터 → 13:00~14:00 방송 정보 표시 ✅
- 30분 데이터도 정확하게 매칭됨

---

#### 4. PROD_DB 필터링

**결정사항**: PROD_DB 선택 시에만 방송 정보 표시

**이유**:
- 실제 프로덕션 DB와의 상관관계만 의미 있음
- DEV_DB, TEST_DB는 방송과 무관

**구현**:
```python
if db_name == 'PROD_DB':
    db_data['broadcast_info'] = db_data['timestamp'].apply(
        lambda ts: get_broadcast_info(ts, broadcast_df)
    )
    customdata = db_data['broadcast_info']
else:
    customdata = None
```

---

## 최근 개발 이력

### 2026-06-19 업데이트

#### 전반부 (기존 기능)
- ✅ Supabase 직접 연결 (CSV에서 변경)
- ✅ 데이터 확장 (6/1~6/15, 2,160개 행)
- ✅ Supabase 페이징 로직 구현
- ✅ Claude AI 요약 기능 추가
- ✅ 조회 가능 기간 표시 (시작~종료)
- ✅ 그래프 x축 자정 날짜 표시
- ✅ Streamlit Cloud 배포 완료
- ✅ Requirements.txt 업데이트

#### 후반부 (TV 편성표 기능)

**1단계: 데이터 준비**
- ✅ Supabase `hnsmall_broadcast` 테이블 생성
- ✅ `generate_broadcast_data.py` 작성
  - 360개 행 생성 (6월 1일~15일, 1시간 단위)
  - 10개 상품별 방송 정보 포함
  - `timestamp`와 `end_time` 컬럼 포함

**2단계: 차트 연동**
- ✅ `get_broadcast_info()` 함수 구현
  - 시간대 범위 매칭 로직
  - 방송 정보 포맷팅
- ✅ CPU, Session, Lock, Alert 차트에 방송 정보 추가
  - Plotly `customdata` 활용
  - Hover 시 방송 정보 표시

**3단계: 필터링 및 UI**
- ✅ PROD_DB 필터링 적용
  - 차트: PROD_DB만 방송 정보 표시
  - 테이블: PROD_DB 선택 시에만 TV편성표 표시
- ✅ TV 편성표 섹션 추가
  - 조회 기간 필터링
  - 데이터 테이블 표시
  - CSV 다운로드 기능

**4단계: 스키마 확정**
- ✅ Supabase 테이블에 `end_time` 컬럼 추가
- ✅ 방송 시간이 다양한 실제 데이터 대응 가능

**5단계: 배포 및 확인**
- ✅ 모든 파일 커밋 및 푸시
- ✅ Streamlit Cloud 자동 배포
- ✅ 실제 화면에서 기능 동작 확인

---

## 기술 결정 요약

| 결정사항 | 이유 | 대안 |
|---------|------|------|
| Supabase 페이징 | 1000행 API 제한 극복 | RLS 활용, GraphQL |
| Claude Opus 모델 | 복잡한 분석 능력 | Claude Sonnet (비용 절감) |
| x축 동적 포맷 | 데이터 범위별 최적화 | 고정 포맷 |
| 범위 매칭 알고리즘 | 30분 데이터 정확성 | 분 단위 무시 |
| PROD_DB 필터링 | 의미 있는 상관관계만 | 모든 DB 표시 |

---

## 향후 개선 사항 (TODO)

- [ ] 실제 홈앤쇼핑 API 연동
- [ ] 방송 시간 자동 예측 (ML)
- [ ] 성능 지표와 방송 상관관계 분석
- [ ] 더 많은 DB 추가
- [ ] 모바일 반응형 디자인
- [ ] 데이터 캐싱 최적화
- [ ] 사용자 설정 저장

---

**관련 문서:**
- [README.md](README.md) - 프로젝트 소개
- [ARCHITECTURE.md](ARCHITECTURE.md) - 기술 아키텍처 및 설정
