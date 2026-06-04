import streamlit as st
import pandas as pd
import re
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="Oracle Alert Log 분석기",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
    <style>
    .critical-alert {
        background-color: #ff4444;
        color: white;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        font-size: 18px;
        font-weight: bold;
    }
    /* 사이드바 버튼 스타일 */
    [data-testid="stSidebar"] button {
        font-size: 12px;
        padding: 8px 12px !important;
        height: auto !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
""", unsafe_allow_html=True)

def load_oracle_errors_from_file():
    """파일에서 Oracle 에러 데이터 로드"""
    errors = {}
    file_path = "oracle_errors_full.txt"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 4:
                code = parts[0]
                name = parts[1]
                cause = parts[2]
                action = parts[3]
                errors[code] = {
                    'name': name,
                    'en_cause': cause,
                    'ko_cause': cause,
                    'en_action': action,
                    'ko_action': action,
                    'critical': False
                }
    except FileNotFoundError:
        pass
    return errors

# 기본 Oracle 에러 정보
ORACLE_ERRORS_DEFAULT = {
    '01555': {'name': 'Snapshot too old', 'en_cause': 'The rollback segment does not have sufficient undo information to satisfy the current SQL statement.', 'ko_cause': '롤백 세그먼트에 현재 SQL 문을 만족할 충분한 언두 정보가 없습니다.', 'en_action': 'Increase the undo retention period or use a larger undo tablespace. Reduce the execution time of long-running queries.', 'ko_action': '언두 보존 기간을 늘리거나 더 큰 언두 테이블스페이스를 사용하세요. 장시간 실행되는 쿼리의 실행 시간을 단축하세요.', 'critical': False},
    '01578': {'name': 'ORACLE data block corrupted', 'en_cause': 'Data block corruption detected in the database.', 'ko_cause': '데이터베이스의 데이터 블록 손상이 감지되었습니다.', 'en_action': 'Run DBVERIFY utility to identify corrupted blocks. Restore from backup or use RMAN recovery.', 'ko_action': 'DBVERIFY 유틸리티를 실행하여 손상된 블록을 식별하세요. 백업에서 복구하거나 RMAN 복구를 사용하세요.', 'critical': True},
    '01650': {'name': 'Unable to extend tablespace', 'en_cause': 'The tablespace has reached its size limit or there is insufficient disk space.', 'ko_cause': '테이블스페이스가 크기 제한에 도달했거나 디스크 공간이 부족합니다.', 'en_action': 'Add a new datafile to the tablespace or extend existing datafiles. Check disk space availability.', 'ko_action': '테이블스페이스에 새 데이터 파일을 추가하거나 기존 데이터 파일을 확장하세요. 디스크 공간 가용성을 확인하세요.', 'critical': True},
    '01658': {'name': 'Unable to create INITIAL extent', 'en_cause': 'Insufficient space to create the initial extent for the segment.', 'ko_cause': '세그먼트의 초기 익스텐트를 생성할 공간이 부족합니다.', 'en_action': 'Add tablespace size or free up unused space. Check for fragmentation in the tablespace.', 'ko_action': '테이블스페이스 크기를 추가하거나 사용하지 않는 공간을 확보하세요. 테이블스페이스의 단편화를 확인하세요.', 'critical': True},
    '16038': {'name': 'Log file corrupted', 'en_cause': 'The log file is corrupted or cannot be read.', 'ko_cause': '로그 파일이 손상되었거나 읽을 수 없습니다.', 'en_action': 'Check the log file integrity. Restore from backup or clear the corrupt redo log group.', 'ko_action': '로그 파일의 무결성을 확인하세요. 백업에서 복구하거나 손상된 리두 로그 그룹을 지우세요.', 'critical': True},
    '04031': {'name': 'Cannot allocate SGA memory', 'en_cause': 'The SGA (System Global Area) cannot allocate required memory.', 'ko_cause': 'SGA(시스템 전역 영역)가 필요한 메모리를 할당할 수 없습니다.', 'en_action': 'Increase SGA size in initialization parameters. Reduce memory-consuming sessions. Increase system RAM.', 'ko_action': '초기화 매개변수에서 SGA 크기를 늘리세요. 메모리를 많이 소비하는 세션을 줄이세요. 시스템 RAM을 늘리세요.', 'critical': True},
    '30951': {'name': 'Archiver error', 'en_cause': 'The archiver process encountered an error while archiving redo log files.', 'ko_cause': '아카이버 프로세스가 리두 로그 파일을 아카이빙할 때 오류가 발생했습니다.', 'en_action': 'Check archive destination space. Verify archiver process is running. Check alert log for details.', 'ko_action': '아카이브 대상 공간을 확인하세요. 아카이버 프로세스가 실행 중인지 확인하세요. 경고 로그에서 세부사항을 확인하세요.', 'critical': True},
    '16014': {'name': 'Log sequence number mismatch', 'en_cause': 'The log sequence numbers do not match between datafile header and redo log.', 'ko_cause': '데이터 파일 헤더와 리두 로그 간의 로그 순서 번호가 일치하지 않습니다.', 'en_action': 'Perform incomplete recovery or use RESETLOGS option. Contact Oracle Support if needed.', 'ko_action': '불완전 복구를 수행하거나 RESETLOGS 옵션을 사용하세요. 필요하면 Oracle 지원팀에 문의하세요.', 'critical': True},
    '27056': {'name': 'Out of memory', 'en_cause': 'The operating system has run out of available memory.', 'ko_cause': '운영 체제의 사용 가능한 메모리가 부족합니다.', 'en_action': 'Increase system RAM. Check for memory leaks. Reduce process memory usage. Restart the instance.', 'ko_action': '시스템 RAM을 늘리세요. 메모리 누수를 확인하세요. 프로세스 메모리 사용을 줄이세요. 인스턴스를 다시 시작하세요.', 'critical': True},
    '00600': {'name': 'Internal consistency check failed', 'en_cause': 'An internal inconsistency has been detected in the Oracle software.', 'ko_cause': 'Oracle 소프트웨어에서 내부 불일치가 감지되었습니다.', 'en_action': 'Collect trace files and contact Oracle Support. Apply relevant patches. Restart the database.', 'ko_action': '트레이스 파일을 수집하고 Oracle 지원팀에 문의하세요. 관련 패치를 적용하세요. 데이터베이스를 다시 시작하세요.', 'critical': True},
    '12514': {'name': 'TNS:listener could not resolve SERVICE_NAME', 'en_cause': 'The listener does not know the service name specified.', 'ko_cause': '리스너가 지정된 서비스 이름을 모릅니다.', 'en_action': 'Check listener.ora configuration. Register the service with the listener. Reload the listener.', 'ko_action': 'listener.ora 설정을 확인하세요. 리스너에 서비스를 등록하세요. 리스너를 다시 로드하세요.', 'critical': False},
    '01017': {'name': 'Invalid username/password', 'en_cause': 'Invalid username or password during login.', 'ko_cause': '로그인 시 사용자명 또는 비밀번호가 잘못되었습니다.', 'en_action': 'Verify the username and password. Check the authentication method. Reset password if needed.', 'ko_action': '사용자명과 비밀번호를 확인하세요. 인증 방법을 확인하세요. 필요시 비밀번호를 재설정하세요.', 'critical': False},
    '01034': {'name': 'ORACLE not available', 'en_cause': 'The Oracle instance is not available or not started.', 'ko_cause': 'Oracle 인스턴스를 사용할 수 없거나 시작되지 않았습니다.', 'en_action': 'Start the database instance. Check alert log for startup errors. Check instance status.', 'ko_action': '데이터베이스 인스턴스를 시작하세요. 시작 오류를 경고 로그에서 확인하세요. 인스턴스 상태를 확인하세요.', 'critical': False},
    '01403': {'name': 'No data found', 'en_cause': 'A SELECT INTO statement returns no rows or a fetch returns no data.', 'ko_cause': 'SELECT INTO 문이 행을 반환하지 않거나 fetch가 데이터를 반환하지 않습니다.', 'en_action': 'Check the query conditions. Verify data exists in the table. Use exception handling.', 'ko_action': '쿼리 조건을 확인하세요. 테이블에 데이터가 있는지 확인하세요. 예외 처리를 사용하세요.', 'critical': False},
}

CRITICAL_ERRORS = {code for code, info in ORACLE_ERRORS_DEFAULT.items() if info['critical']}
ORACLE_ERRORS = ORACLE_ERRORS_DEFAULT.copy()
ORACLE_ERRORS.update(load_oracle_errors_from_file())

def extract_ora_errors(text):
    pattern = r'(?:ORA-)?(\d{5})(?:[:\s]([^\n]*)?)?'
    matches = re.findall(pattern, text, re.MULTILINE)
    errors = []
    for code, message in matches:
        is_found = code in ORACLE_ERRORS
        error_info = ORACLE_ERRORS.get(code, {'name': 'Unknown error', 'en_cause': 'No information available.', 'ko_cause': '정보 없음', 'en_action': 'Check Oracle documentation.', 'ko_action': 'Oracle 문서 확인', 'critical': False})
        errors.append({'Error Code': f'ORA-{code}', 'Name': error_info['name'], 'Message': message.strip() if message else '', 'Code': code, 'Critical': code in CRITICAL_ERRORS, 'Info': error_info, 'Found': is_found})
    return errors

def get_oracle_doc_url(ora_code):
    return f"https://docs.oracle.com/search/?q={ora_code}&book=DBERR&library=en%2Ferror-help"

st.title("🔍 Oracle Alert Log 분석기")
st.markdown("---")

with st.sidebar:
    st.header("🔎 에러 검색")
    search_query = st.text_input("에러 코드 또는 에러명 검색:", placeholder="01555 또는 Snapshot")

    filtered_errors = [(code, info) for code, info in ORACLE_ERRORS.items() if (search_query.lower() in code or search_query.lower() in info['name'].lower())] if search_query else list(ORACLE_ERRORS.items())
    filtered_errors.sort(key=lambda x: x[0])

    page_size = 10
    total_pages = (len(filtered_errors) + page_size - 1) // page_size

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'prev_search_query' not in st.session_state:
        st.session_state.prev_search_query = search_query
    if st.session_state.prev_search_query != search_query:
        st.session_state.current_page = 1
        st.session_state.prev_search_query = search_query

    start_idx = (st.session_state.current_page - 1) * page_size
    end_idx = start_idx + page_size
    page_errors = filtered_errors[start_idx:end_idx]

    st.markdown(f"**검색 결과: {len(filtered_errors)}개**")
    st.markdown(f"**페이지: {st.session_state.current_page}/{total_pages}**")

    for code, info in page_errors:
        critical_badge = "🔴" if code in CRITICAL_ERRORS else "🟡"
        error_name = info['name'][:18]
        if st.button(f"{critical_badge} {code} {error_name}", key=f"btn_{code}", use_container_width=True):
            st.session_state.selected_error_code = code

    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ 이전", disabled=(st.session_state.current_page <= 1), use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
    with col2:
        st.markdown(f"<div style='text-align: center; padding-top: 8px;'>{st.session_state.current_page} / {total_pages}</div>", unsafe_allow_html=True)
    with col3:
        if st.button("다음 ▶", disabled=(st.session_state.current_page >= total_pages), use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("📋 Alert Log 입력")
    alert_log_text = st.text_area("Oracle Alert Log 내용을 입력하세요:", height=150, placeholder="ORA-01489 또는 01489\nORA-16038: log file corrupted\n00600")
    col1, col2 = st.columns(2)
    with col1:
        analyze_button = st.button("🔍 분석하기", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ 초기화", use_container_width=True)
    if clear_button:
        st.rerun()

with col_right:
    if 'selected_error_code' in st.session_state:
        error_code = st.session_state.selected_error_code
        if error_code in ORACLE_ERRORS:
            error_info = ORACLE_ERRORS[error_code]
            st.subheader(f"ORA-{error_code}")
            with st.container(border=True):
                st.markdown(f"**{error_info['name']}**")
                if error_code in CRITICAL_ERRORS:
                    st.warning("🔴 크리티컬 에러")
                else:
                    st.info("🟡 일반 에러")
                st.markdown("**원인**")
                st.caption(error_info['en_cause'][:100] + "...")
                st.markdown("**조치**")
                st.caption(error_info['en_action'][:100] + "...")
    else:
        st.info("👈 왼쪽 사이드바에서 에러를 검색하여 선택하면 상세정보가 표시됩니다.")

if analyze_button and alert_log_text.strip():
    errors = extract_ora_errors(alert_log_text)
    with col_left:
        if not errors:
            st.warning("⚠️ ORA- 에러를 찾을 수 없습니다.")
        else:
            critical_errors = [e for e in errors if e['Critical']]
            if critical_errors:
                st.markdown(f"<div class='critical-alert'>⚠️ 크리티컬 에러 발견! ({len(critical_errors)}개)<br>즉시 조치가 필요합니다!</div>", unsafe_allow_html=True)
                st.markdown("### 🚨 크리티컬 에러 조치 가이드")
                for error in critical_errors:
                    with st.expander(f"**ORA-{error['Code']}** - {error['Name']}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 📌 원인 (Cause)")
                            st.info(f"🇬🇧 {error['Info']['en_cause']}")
                            st.info(f"🇰🇷 {error['Info']['ko_cause']}")
                        with col2:
                            st.markdown("#### ✅ 조치 (Action)")
                            st.success(f"🇬🇧 {error['Info']['en_action']}")
                            st.success(f"🇰🇷 {error['Info']['ko_action']}")
                        st.markdown(f"📖 [Oracle 공식 문서 보기]({get_oracle_doc_url(error['Code'])})")

            st.markdown("### 📊 발견된 모든 에러 목록")
            table_data = [{'순번': i, '에러 코드': error['Error Code'], '에러명': error['Name'], '심각도': '🔴 크리티컬' if error['Critical'] else '🟡 일반', '메시지': error['Message'][:50] + '...' if len(error['Message']) > 50 else error['Message']} for i, error in enumerate(errors, 1)]
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True, column_config={'순번': st.column_config.NumberColumn(width=60), '에러 코드': st.column_config.TextColumn(width=100), '에러명': st.column_config.TextColumn(width=150), '심각도': st.column_config.TextColumn(width=100), '메시지': st.column_config.TextColumn(width=300)})

            st.markdown("### 📈 분석 요약")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("전체 에러 수", len(errors))
            with col2:
                st.metric("크리티컬 에러", len(critical_errors), delta="높음" if critical_errors else "정상")
            with col3:
                st.metric("일반 에러", len(errors) - len(critical_errors))
            with col4:
                st.metric("분석 일시", datetime.now().strftime("%H:%M:%S"))

elif analyze_button and not alert_log_text.strip():
    with col_left:
        st.error("❌ Alert Log 텍스트를 입력해주세요.")

st.markdown("---")
st.markdown("### 💡 사용 방법\n1. **왼쪽 사이드바**: 에러 코드 검색 → 클릭하면 오른쪽에 상세정보 표시\n2. **Alert Log 입력**: 분석할 로그 텍스트 입력\n3. **분석하기**: 발견된 모든 에러와 조치 가이드 확인\n4. **필요시**: Oracle 공식 문서 링크로 추가 정보 조회")
