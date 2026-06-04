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
    .error-row {
        padding: 10px;
        border-bottom: 1px solid #ddd;
    }
    .ora-number {
        font-family: monospace;
        font-weight: bold;
        color: #0066cc;
    }
    </style>
""", unsafe_allow_html=True)

# Oracle 에러 정보 데이터베이스
ORACLE_ERRORS = {
    '01555': {
        'name': 'Snapshot too old',
        'en_cause': 'The rollback segment does not have sufficient undo information to satisfy the current SQL statement.',
        'ko_cause': '롤백 세그먼트에 현재 SQL 문을 만족할 충분한 언두 정보가 없습니다.',
        'en_action': 'Increase the undo retention period or use a larger undo tablespace. Reduce the execution time of long-running queries.',
        'ko_action': '언두 보존 기간을 늘리거나 더 큰 언두 테이블스페이스를 사용하세요. 장시간 실행되는 쿼리의 실행 시간을 단축하세요.',
        'critical': False
    },
    '01578': {
        'name': 'ORACLE data block corrupted',
        'en_cause': 'Data block corruption detected in the database.',
        'ko_cause': '데이터베이스의 데이터 블록 손상이 감지되었습니다.',
        'en_action': 'Run DBVERIFY utility to identify corrupted blocks. Restore from backup or use RMAN recovery.',
        'ko_action': 'DBVERIFY 유틸리티를 실행하여 손상된 블록을 식별하세요. 백업에서 복구하거나 RMAN 복구를 사용하세요.',
        'critical': True
    },
    '01650': {
        'name': 'Unable to extend tablespace',
        'en_cause': 'The tablespace has reached its size limit or there is insufficient disk space.',
        'ko_cause': '테이블스페이스가 크기 제한에 도달했거나 디스크 공간이 부족합니다.',
        'en_action': 'Add a new datafile to the tablespace or extend existing datafiles. Check disk space availability.',
        'ko_action': '테이블스페이스에 새 데이터 파일을 추가하거나 기존 데이터 파일을 확장하세요. 디스크 공간 가용성을 확인하세요.',
        'critical': True
    },
    '01658': {
        'name': 'Unable to create INITIAL extent',
        'en_cause': 'Insufficient space to create the initial extent for the segment.',
        'ko_cause': '세그먼트의 초기 익스텐트를 생성할 공간이 부족합니다.',
        'en_action': 'Add tablespace size or free up unused space. Check for fragmentation in the tablespace.',
        'ko_action': '테이블스페이스 크기를 추가하거나 사용하지 않는 공간을 확보하세요. 테이블스페이스의 단편화를 확인하세요.',
        'critical': True
    },
    '16038': {
        'name': 'Log file corrupted',
        'en_cause': 'The log file is corrupted or cannot be read.',
        'ko_cause': '로그 파일이 손상되었거나 읽을 수 없습니다.',
        'en_action': 'Check the log file integrity. Restore from backup or clear the corrupt redo log group.',
        'ko_action': '로그 파일의 무결성을 확인하세요. 백업에서 복구하거나 손상된 리두 로그 그룹을 지우세요.',
        'critical': True
    },
    '04031': {
        'name': 'Cannot allocate SGA memory',
        'en_cause': 'The SGA (System Global Area) cannot allocate required memory.',
        'ko_cause': 'SGA(시스템 전역 영역)가 필요한 메모리를 할당할 수 없습니다.',
        'en_action': 'Increase SGA size in initialization parameters. Reduce memory-consuming sessions. Increase system RAM.',
        'ko_action': '초기화 매개변수에서 SGA 크기를 늘리세요. 메모리를 많이 소비하는 세션을 줄이세요. 시스템 RAM을 늘리세요.',
        'critical': True
    },
    '30951': {
        'name': 'Archiver error',
        'en_cause': 'The archiver process encountered an error while archiving redo log files.',
        'ko_cause': '아카이버 프로세스가 리두 로그 파일을 아카이빙할 때 오류가 발생했습니다.',
        'en_action': 'Check archive destination space. Verify archiver process is running. Check alert log for details.',
        'ko_action': '아카이브 대상 공간을 확인하세요. 아카이버 프로세스가 실행 중인지 확인하세요. 경고 로그에서 세부사항을 확인하세요.',
        'critical': True
    },
    '16014': {
        'name': 'Log sequence number mismatch',
        'en_cause': 'The log sequence numbers do not match between datafile header and redo log.',
        'ko_cause': '데이터 파일 헤더와 리두 로그 간의 로그 순서 번호가 일치하지 않습니다.',
        'en_action': 'Perform incomplete recovery or use RESETLOGS option. Contact Oracle Support if needed.',
        'ko_action': '불완전 복구를 수행하거나 RESETLOGS 옵션을 사용하세요. 필요하면 Oracle 지원팀에 문의하세요.',
        'critical': True
    },
    '27056': {
        'name': 'Out of memory',
        'en_cause': 'The operating system has run out of available memory.',
        'ko_cause': '운영 체제의 사용 가능한 메모리가 부족합니다.',
        'en_action': 'Increase system RAM. Check for memory leaks. Reduce process memory usage. Restart the instance.',
        'ko_action': '시스템 RAM을 늘리세요. 메모리 누수를 확인하세요. 프로세스 메모리 사용을 줄이세요. 인스턴스를 다시 시작하세요.',
        'critical': True
    },
    '00600': {
        'name': 'Internal consistency check failed',
        'en_cause': 'An internal inconsistency has been detected in the Oracle software.',
        'ko_cause': 'Oracle 소프트웨어에서 내부 불일치가 감지되었습니다.',
        'en_action': 'Collect trace files and contact Oracle Support. Apply relevant patches. Restart the database.',
        'ko_action': '트레이스 파일을 수집하고 Oracle 지원팀에 문의하세요. 관련 패치를 적용하세요. 데이터베이스를 다시 시작하세요.',
        'critical': True
    },
    '12514': {
        'name': 'TNS:listener could not resolve SERVICE_NAME',
        'en_cause': 'The listener does not know the service name specified.',
        'ko_cause': '리스너가 지정된 서비스 이름을 모릅니다.',
        'en_action': 'Check listener.ora configuration. Register the service with the listener. Reload the listener.',
        'ko_action': 'listener.ora 설정을 확인하세요. 리스너에 서비스를 등록하세요. 리스너를 다시 로드하세요.',
        'critical': False
    },
    '01017': {
        'name': 'Invalid username/password',
        'en_cause': 'Invalid username or password during login.',
        'ko_cause': '로그인 시 사용자명 또는 비밀번호가 잘못되었습니다.',
        'en_action': 'Verify the username and password. Check the authentication method. Reset password if needed.',
        'ko_action': '사용자명과 비밀번호를 확인하세요. 인증 방법을 확인하세요. 필요시 비밀번호를 재설정하세요.',
        'critical': False
    },
    '01034': {
        'name': 'ORACLE not available',
        'en_cause': 'The Oracle instance is not available or not started.',
        'ko_cause': 'Oracle 인스턴스를 사용할 수 없거나 시작되지 않았습니다.',
        'en_action': 'Start the database instance. Check alert log for startup errors. Check instance status.',
        'ko_action': '데이터베이스 인스턴스를 시작하세요. 시작 오류를 경고 로그에서 확인하세요. 인스턴스 상태를 확인하세요.',
        'critical': False
    },
    '01403': {
        'name': 'No data found',
        'en_cause': 'A SELECT INTO statement returns no rows or a fetch returns no data.',
        'ko_cause': 'SELECT INTO 문이 행을 반환하지 않거나 fetch가 데이터를 반환하지 않습니다.',
        'en_action': 'Check the query conditions. Verify data exists in the table. Use exception handling.',
        'ko_action': '쿼리 조건을 확인하세요. 테이블에 데이터가 있는지 확인하세요. 예외 처리를 사용하세요.',
        'critical': False
    },
    '01422': {
        'name': 'Exact fetch returns more than requested rows',
        'en_cause': 'SELECT INTO returns more than one row when exactly one was expected.',
        'ko_cause': 'SELECT INTO이 정확히 하나의 행을 기대했을 때 하나 이상의 행을 반환했습니다.',
        'en_action': 'Use BULK COLLECT or a cursor. Modify WHERE clause to return exactly one row. Use exception handling.',
        'ko_action': 'BULK COLLECT 또는 커서를 사용하세요. WHERE 절을 수정하여 정확히 하나의 행을 반환하도록 하세요.',
        'critical': False
    },
    '01438': {
        'name': 'Value larger than specified precision',
        'en_cause': 'A numeric value is larger than the precision of the column allows.',
        'ko_cause': '숫자 값이 열의 정밀도보다 큽니다.',
        'en_action': 'Check the numeric value. Increase column precision. Reduce the input value.',
        'ko_action': '숫자 값을 확인하세요. 열의 정밀도를 늘리세요. 입력 값을 줄이세요.',
        'critical': False
    },
    '01722': {
        'name': 'Invalid number',
        'en_cause': 'A character string was not a valid number.',
        'ko_cause': '문자 문자열이 유효한 숫자가 아닙니다.',
        'en_action': 'Verify the data format. Use TO_NUMBER with error handling. Check for non-numeric characters.',
        'ko_action': '데이터 형식을 확인하세요. 오류 처리와 함께 TO_NUMBER를 사용하세요. 숫자가 아닌 문자를 확인하세요.',
        'critical': False
    },
    '01476': {
        'name': 'Divisor is equal to zero',
        'en_cause': 'A division by zero was attempted.',
        'ko_cause': '0으로 나누기를 시도했습니다.',
        'en_action': 'Add a check for zero divisor. Use CASE or IF statements. Handle exception.',
        'ko_action': '0으로 나누기를 확인하세요. CASE 또는 IF 문을 사용하세요. 예외를 처리하세요.',
        'critical': False
    },
    '02290': {
        'name': 'Check constraint violated',
        'en_cause': 'A CHECK constraint was violated.',
        'ko_cause': 'CHECK 제약 조건이 위반되었습니다.',
        'en_action': 'Verify the data against constraint conditions. Modify the data to satisfy constraints.',
        'ko_action': '제약 조건에 대한 데이터를 확인하세요. 제약 조건을 만족하도록 데이터를 수정하세요.',
        'critical': False
    },
    '02291': {
        'name': 'Integrity constraint violated - parent key not found',
        'en_cause': 'A FOREIGN KEY constraint was violated - parent key does not exist.',
        'ko_cause': 'FOREIGN KEY 제약 조건 위반 - 부모 키가 없습니다.',
        'en_action': 'Insert the parent record first. Verify the referenced table. Check constraint definition.',
        'ko_action': '먼저 부모 레코드를 삽입하세요. 참조된 테이블을 확인하세요. 제약 조건 정의를 확인하세요.',
        'critical': False
    },
    '02292': {
        'name': 'Integrity constraint violated - child record found',
        'en_cause': 'A FOREIGN KEY constraint was violated - child records exist.',
        'ko_cause': 'FOREIGN KEY 제약 조건 위반 - 자식 레코드가 있습니다.',
        'en_action': 'Delete child records first. Disable constraint if needed. Check referencing tables.',
        'ko_action': '먼저 자식 레코드를 삭제하세요. 필요시 제약 조건을 비활성화하세요. 참조하는 테이블을 확인하세요.',
        'critical': False
    },
    '02449': {
        'name': 'Cannot drop table - foreign key constraint',
        'en_cause': 'A table cannot be dropped because other tables reference it.',
        'ko_cause': '다른 테이블이 참조하므로 테이블을 삭제할 수 없습니다.',
        'en_action': 'Drop dependent tables first. Disable foreign key constraints. Drop constraints before table.',
        'ko_action': '먼저 종속 테이블을 삭제하세요. 외래 키 제약 조건을 비활성화하세요. 테이블 전에 제약 조건을 삭제하세요.',
        'critical': False
    },
    '04043': {
        'name': 'Object does not exist',
        'en_cause': 'The referenced object (table, view, procedure, etc.) does not exist.',
        'ko_cause': '참조된 객체(테이블, 뷰, 프로시저 등)가 없습니다.',
        'en_action': 'Check the object name spelling. Verify schema/owner. Create the object if missing.',
        'ko_action': '객체명 철자를 확인하세요. 스키마/소유자를 확인하세요. 누락된 객체를 생성하세요.',
        'critical': False
    },
    '06502': {
        'name': 'PL/SQL: Numeric or value error',
        'en_cause': 'A conversion, truncation, or arithmetic error occurred in PL/SQL.',
        'ko_cause': 'PL/SQL에서 변환, 절단 또는 산술 오류가 발생했습니다.',
        'en_action': 'Check variable types and values. Use TO_NUMBER, TO_CHAR for conversion. Validate input.',
        'ko_action': '변수 타입과 값을 확인하세요. 변환을 위해 TO_NUMBER, TO_CHAR를 사용하세요. 입력을 검증하세요.',
        'critical': False
    },
    '06550': {
        'name': 'PL/SQL: Syntax error',
        'en_cause': 'A syntax error was found in PL/SQL code.',
        'ko_cause': 'PL/SQL 코드에서 문법 오류가 발견되었습니다.',
        'en_action': 'Check PL/SQL syntax. Review the error line number. Validate SQL statements.',
        'ko_action': 'PL/SQL 문법을 확인하세요. 오류 줄 번호를 검토하세요. SQL 문을 검증하세요.',
        'critical': False
    },
    '12528': {
        'name': 'TNS:Listener - all appropriate instances blocked',
        'en_cause': 'The listener could not connect to the database instance.',
        'ko_cause': '리스너가 데이터베이스 인스턴스에 연결할 수 없습니다.',
        'en_action': 'Start the database instance. Check instance status. Review listener.ora configuration.',
        'ko_action': '데이터베이스 인스턴스를 시작하세요. 인스턴스 상태를 확인하세요. listener.ora 설정을 검토하세요.',
        'critical': False
    },
    '12545': {
        'name': 'Connect failed because target host or object does not exist',
        'en_cause': 'Cannot connect to the specified host or database.',
        'ko_cause': '지정된 호스트 또는 데이터베이스에 연결할 수 없습니다.',
        'en_action': 'Check hostname and port. Verify network connectivity. Check firewall settings.',
        'ko_action': '호스트명과 포트를 확인하세요. 네트워크 연결을 확인하세요. 방화벽 설정을 확인하세요.',
        'critical': False
    },
    '12704': {
        'name': 'Character set mismatch',
        'en_cause': 'The character set of the client does not match the database.',
        'ko_cause': '클라이언트의 문자 집합이 데이터베이스와 일치하지 않습니다.',
        'en_action': 'Set NLS_LANG environment variable. Match client and database character sets.',
        'ko_action': 'NLS_LANG 환경 변수를 설정하세요. 클라이언트 및 데이터베이스 문자 집합을 일치시키세요.',
        'critical': False
    },
    '14402': {
        'name': 'Updating partition key column',
        'en_cause': 'An attempt was made to update a partition key column.',
        'ko_cause': '파티션 키 열을 업데이트하려고 시도했습니다.',
        'en_action': 'Delete and re-insert the row instead. Enable ENABLE ROW MOVEMENT if needed.',
        'ko_action': '대신 행을 삭제하고 다시 삽입하세요. 필요시 ENABLE ROW MOVEMENT를 사용하세요.',
        'critical': False
    },
    '20000': {
        'name': 'User-defined exception',
        'en_cause': 'A user-defined exception was raised by the application.',
        'ko_cause': '애플리케이션이 사용자 정의 예외를 발생시켰습니다.',
        'en_action': 'Check application logic. Review error message. Verify business rules.',
        'ko_action': '애플리케이션 로직을 확인하세요. 오류 메시지를 검토하세요. 비즈니스 규칙을 확인하세요.',
        'critical': False
    },
    '01401': {
        'name': 'Inserted value too large for column',
        'en_cause': 'The value being inserted is longer than the column size allows.',
        'ko_cause': '삽입하려는 값이 열 크기보다 큽니다.',
        'en_action': 'Check the value length. Increase column size. Truncate or modify the value.',
        'ko_action': '값의 길이를 확인하세요. 열 크기를 늘리세요. 값을 자르거나 수정하세요.',
        'critical': False
    },
    '01445': {
        'name': 'Cannot select ROWID from view',
        'en_cause': 'ROWID cannot be selected from a view without a base table.',
        'ko_cause': '기본 테이블이 없는 뷰에서 ROWID를 선택할 수 없습니다.',
        'en_action': 'Use rownum instead of ROWID. Modify the view to include base table. Use WITH READ ONLY.',
        'ko_action': 'ROWID 대신 rownum을 사용하세요. 기본 테이블을 포함하도록 뷰를 수정하세요.',
        'critical': False
    },
    '01489': {
        'name': 'Result of string concatenation too long',
        'en_cause': 'The result of concatenating strings exceeds the maximum length.',
        'ko_cause': '문자열 연결 결과가 최대 길이를 초과합니다.',
        'en_action': 'Use a larger data type (CLOB). Split concatenation. Reduce string lengths.',
        'ko_action': '더 큰 데이터 타입(CLOB)을 사용하세요. 연결을 분할하세요. 문자열 길이를 줄이세요.',
        'critical': False
    },
    '01747': {
        'name': 'Invalid user.table.column name',
        'en_cause': 'The table or column name is invalid or does not exist.',
        'ko_cause': '테이블 또는 열 이름이 유효하지 않거나 없습니다.',
        'en_action': 'Check table and column names. Verify schema. Quote reserved words if needed.',
        'ko_action': '테이블 및 열 이름을 확인하세요. 스키마를 확인하세요. 필요시 예약어를 인용하세요.',
        'critical': False
    },
    '01789': {
        'name': 'Query block has incorrect number of result columns',
        'en_cause': 'UNION queries have different number of columns.',
        'ko_cause': 'UNION 쿼리의 열 개수가 다릅니다.',
        'en_action': 'Make sure all SELECT statements have the same number of columns. Align column order.',
        'ko_action': '모든 SELECT 문이 같은 수의 열을 가지도록 하세요. 열 순서를 맞추세요.',
        'critical': False
    },
    '04000': {
        'name': 'Invalid ALTER TABLE option',
        'en_cause': 'An invalid option was used in an ALTER TABLE statement.',
        'ko_cause': 'ALTER TABLE 문에서 유효하지 않은 옵션이 사용되었습니다.',
        'en_action': 'Check ALTER TABLE syntax. Review Oracle documentation. Correct the option used.',
        'ko_action': 'ALTER TABLE 문법을 확인하세요. Oracle 문서를 검토하세요. 사용된 옵션을 수정하세요.',
        'critical': False
    },
    '04061': {
        'name': 'Existing state of package has been discarded',
        'en_cause': 'The package was invalidated and its state was discarded.',
        'ko_cause': '패키지가 무효화되어 상태가 삭제되었습니다.',
        'en_action': 'Recompile the package. Check for compilation errors. Reload the package.',
        'ko_action': '패키지를 다시 컴파일하세요. 컴파일 오류를 확인하세요. 패키지를 다시 로드하세요.',
        'critical': False
    },
    '07314': {
        'name': 'Insufficient memory',
        'en_cause': 'The system or Oracle process has run out of memory.',
        'ko_cause': '시스템 또는 Oracle 프로세스의 메모리가 부족합니다.',
        'en_action': 'Increase virtual memory. Close unnecessary applications. Increase swap space.',
        'ko_action': '가상 메모리를 늘리세요. 불필요한 애플리케이션을 닫으세요. 스왑 공간을 늘리세요.',
        'critical': False
    },
    '22816': {
        'name': 'Unsupported feature with RETURNING clause',
        'en_cause': 'The RETURNING clause is used with an unsupported feature.',
        'ko_cause': 'RETURNING 절이 지원되지 않는 기능과 함께 사용되었습니다.',
        'en_action': 'Remove RETURNING clause if not supported. Use alternate method to get values.',
        'ko_action': '지원되지 않으면 RETURNING 절을 제거하세요. 값을 가져올 대체 방법을 사용하세요.',
        'critical': False
    },
    '01000': {
        'name': 'Maximum open cursors exceeded',
        'en_cause': 'The number of open cursors exceeds the OPEN_CURSORS parameter.',
        'ko_cause': '열린 커서의 개수가 OPEN_CURSORS 매개변수를 초과했습니다.',
        'en_action': 'Close unused cursors. Increase OPEN_CURSORS parameter. Check for cursor leaks in application.',
        'ko_action': '사용하지 않는 커서를 닫으세요. OPEN_CURSORS 매개변수를 늘리세요. 애플리케이션의 커서 누수를 확인하세요.',
        'critical': False
    },
    '01012': {
        'name': 'Not logged on',
        'en_cause': 'No database connection established.',
        'ko_cause': '데이터베이스 연결이 확립되지 않았습니다.',
        'en_action': 'Establish a connection to the database. Check authentication credentials. Verify session status.',
        'ko_action': '데이터베이스 연결을 확립하세요. 인증 자격증명을 확인하세요. 세션 상태를 확인하세요.',
        'critical': False
    },
    '01031': {
        'name': 'Insufficient privileges',
        'en_cause': 'The user does not have the required privileges to perform the operation.',
        'ko_cause': '사용자가 작업을 수행하는 데 필요한 권한이 없습니다.',
        'en_action': 'Grant required privileges to the user. Check role assignments. Contact DBA.',
        'ko_action': '사용자에게 필요한 권한을 부여하세요. 역할 할당을 확인하세요. DBA에 문의하세요.',
        'critical': False
    },
    '01033': {
        'name': 'ORACLE initialization or shutdown in progress',
        'en_cause': 'The database is in the process of initializing or shutting down.',
        'ko_cause': '데이터베이스가 초기화 또는 종료 중입니다.',
        'en_action': 'Wait for the database to complete startup or shutdown. Check alert log. Verify instance status.',
        'ko_action': '데이터베이스가 시작 또는 종료를 완료할 때까지 기다리세요. 경고 로그를 확인하세요. 인스턴스 상태를 확인하세요.',
        'critical': False
    },
    '01041': {
        'name': 'Internal error - hostdef extension missing',
        'en_cause': 'The host definition extension is missing or corrupted.',
        'ko_cause': '호스트 정의 확장이 누락되었거나 손상되었습니다.',
        'en_action': 'Reinstall Oracle client software. Check installation files. Contact Oracle Support.',
        'ko_action': 'Oracle 클라이언트 소프트웨어를 다시 설치하세요. 설치 파일을 확인하세요. Oracle 지원팀에 문의하세요.',
        'critical': False
    },
    '01051': {
        'name': 'ORACLE procedure tables corrupted',
        'en_cause': 'The Oracle procedure tables or system area is corrupted.',
        'ko_cause': 'Oracle 프로시저 테이블 또는 시스템 영역이 손상되었습니다.',
        'en_action': 'Restore from backup. Run DBVERIFY. Contact Oracle Support. Reinstall if necessary.',
        'ko_action': '백업에서 복구하세요. DBVERIFY를 실행하세요. Oracle 지원팀에 문의하세요. 필요시 다시 설치하세요.',
        'critical': False
    },
    '01075': {
        'name': 'You are not connected to ORACLE',
        'en_cause': 'There is no active connection to the Oracle database.',
        'ko_cause': 'Oracle 데이터베이스에 활성 연결이 없습니다.',
        'en_action': 'Connect to the database. Check connection string. Verify listener status.',
        'ko_action': '데이터베이스에 연결하세요. 연결 문자열을 확인하세요. 리스너 상태를 확인하세요.',
        'critical': False
    },
    '01109': {
        'name': 'Database not open',
        'en_cause': 'The database is not open or not in a valid state.',
        'ko_cause': '데이터베이스가 열려 있지 않거나 유효한 상태가 아닙니다.',
        'en_action': 'Open the database. Mount the database. Check initialization parameters. Perform recovery if needed.',
        'ko_action': '데이터베이스를 열으세요. 데이터베이스를 마운트하세요. 초기화 매개변수를 확인하세요. 필요시 복구를 수행하세요.',
        'critical': False
    },
    '01110': {
        'name': 'Data file not open',
        'en_cause': 'A data file is offline or cannot be opened.',
        'ko_cause': '데이터 파일이 오프라인이거나 열 수 없습니다.',
        'en_action': 'Bring the datafile online. Check file permissions. Verify file location. Run recovery if needed.',
        'ko_action': '데이터 파일을 온라인으로 전환하세요. 파일 권한을 확인하세요. 파일 위치를 확인하세요. 필요시 복구를 수행하세요.',
        'critical': False
    },
    '01552': {
        'name': 'Non-system tablespace contains data from multiple databases',
        'en_cause': 'A tablespace contains data from more than one database.',
        'ko_cause': '테이블스페이스에 하나 이상의 데이터베이스의 데이터가 포함되어 있습니다.',
        'en_action': 'Restore affected datafiles from correct database backup. Verify data integrity.',
        'ko_action': '영향을 받는 데이터 파일을 올바른 데이터베이스 백업에서 복구하세요. 데이터 무결성을 확인하세요.',
        'critical': False
    },
    '01553': {
        'name': 'Tablespace not empty - cannot drop',
        'en_cause': 'The tablespace contains objects and cannot be dropped.',
        'ko_cause': '테이블스페이스에 객체가 있어 삭제할 수 없습니다.',
        'en_action': 'Move objects to another tablespace. Drop all objects first. Use DROP TABLESPACE ... INCLUDING CONTENTS.',
        'ko_action': '객체를 다른 테이블스페이스로 이동하세요. 먼저 모든 객체를 삭제하세요. DROP TABLESPACE ... INCLUDING CONTENTS를 사용하세요.',
        'critical': False
    },
    '01562': {
        'name': 'UNDO tablespace cannot be read only',
        'en_cause': 'An attempt was made to make UNDO tablespace read-only.',
        'ko_cause': 'UNDO 테이블스페이스를 읽기 전용으로 만들려고 시도했습니다.',
        'en_action': 'Keep UNDO tablespace in read-write mode. Use different tablespace for read-only data.',
        'ko_action': 'UNDO 테이블스페이스를 읽기-쓰기 모드로 유지하세요. 읽기 전용 데이터에 다른 테이블스페이스를 사용하세요.',
        'critical': False
    },
    '01744': {
        'name': 'Illegal base type for REF type',
        'en_cause': 'Invalid base type specified for a REF type column.',
        'ko_cause': 'REF 타입 열에 대해 유효하지 않은 기본 타입이 지정되었습니다.',
        'en_action': 'Use valid object type for REF. Check data type definition. Verify schema.',
        'ko_action': 'REF에 유효한 객체 타입을 사용하세요. 데이터 타입 정의를 확인하세요. 스키마를 확인하세요.',
        'critical': False
    },
    '01746': {
        'name': 'Column alias needed for expression in ORDER BY',
        'en_cause': 'An expression in ORDER BY clause needs a column alias.',
        'ko_cause': 'ORDER BY 절의 식에 열 별칭이 필요합니다.',
        'en_action': 'Add column alias for the expression. Use column position number. Simplify the expression.',
        'ko_action': '식에 열 별칭을 추가하세요. 열 위치 번호를 사용하세요. 식을 단순화하세요.',
        'critical': False
    },
    '01748': {
        'name': 'Only simple column names allowed',
        'en_cause': 'Complex expressions not allowed in this context.',
        'ko_cause': '이 컨텍스트에서 복잡한 식이 허용되지 않습니다.',
        'en_action': 'Use simple column names. Use subquery if expression needed. Check syntax.',
        'ko_action': '간단한 열 이름을 사용하세요. 식이 필요하면 서브쿼리를 사용하세요. 문법을 확인하세요.',
        'critical': False
    },
    '01752': {
        'name': 'Cannot delete from view without key-preserved table',
        'en_cause': 'View deletion requires a key-preserved base table.',
        'ko_cause': '뷰 삭제에는 키-보존된 기본 테이블이 필요합니다.',
        'en_action': 'Use INSTEAD OF trigger for view. Modify view definition. Delete from base table instead.',
        'ko_action': '뷰에 INSTEAD OF 트리거를 사용하세요. 뷰 정의를 수정하세요. 대신 기본 테이블에서 삭제하세요.',
        'critical': False
    },
    '01753': {
        'name': 'Column definition length too big',
        'en_cause': 'The definition of a column is too long.',
        'ko_cause': '열의 정의가 너무 깁니다.',
        'en_action': 'Reduce column size. Use shorter column name. Simplify constraint definition.',
        'ko_action': '열 크기를 줄이세요. 더 짧은 열 이름을 사용하세요. 제약 조건 정의를 단순화하세요.',
        'critical': False
    },
    '01754': {
        'name': 'Table may contain only one LONG column',
        'en_cause': 'An attempt was made to add a second LONG column to a table.',
        'ko_cause': '테이블에 두 번째 LONG 열을 추가하려고 시도했습니다.',
        'en_action': 'Use CLOB instead of LONG. Remove existing LONG column. Use LOB column type.',
        'ko_action': 'LONG 대신 CLOB을 사용하세요. 기존 LONG 열을 제거하세요. LOB 열 타입을 사용하세요.',
        'critical': False
    },
    '01759': {
        'name': 'Invalid trigger event',
        'en_cause': 'The trigger event specified is invalid.',
        'ko_cause': '지정된 트리거 이벤트가 유효하지 않습니다.',
        'en_action': 'Use valid trigger events: INSERT, UPDATE, DELETE. Check trigger definition.',
        'ko_action': '유효한 트리거 이벤트 사용: INSERT, UPDATE, DELETE. 트리거 정의를 확인하세요.',
        'critical': False
    },
    '01760': {
        'name': 'Illegal argument for function',
        'en_cause': 'An invalid argument was passed to a function.',
        'ko_cause': '함수에 유효하지 않은 인수가 전달되었습니다.',
        'en_action': 'Check function documentation. Verify argument types. Use correct argument values.',
        'ko_action': '함수 문서를 확인하세요. 인수 타입을 확인하세요. 올바른 인수 값을 사용하세요.',
        'critical': False
    },
    '01776': {
        'name': 'Cannot modify more than one base table through view',
        'en_cause': 'The view references multiple base tables and cannot be updated.',
        'ko_cause': '뷰가 여러 기본 테이블을 참조하고 업데이트할 수 없습니다.',
        'en_action': 'Use INSTEAD OF trigger. Modify view definition. Update base tables directly.',
        'ko_action': 'INSTEAD OF 트리거를 사용하세요. 뷰 정의를 수정하세요. 기본 테이블을 직접 업데이트하세요.',
        'critical': False
    },
    '01781': {
        'name': 'ROWID not permitted',
        'en_cause': 'ROWID cannot be used in this context.',
        'ko_cause': '이 컨텍스트에서 ROWID를 사용할 수 없습니다.',
        'en_action': 'Use rownum or primary key instead. Remove ROWID reference. Use alternate identification.',
        'ko_action': '대신 rownum 또는 기본 키를 사용하세요. ROWID 참조를 제거하세요. 대체 식별을 사용하세요.',
        'critical': False
    },
    '01830': {
        'name': 'Date format picture ends before converting entire input string',
        'en_cause': 'The date format does not match the input string length.',
        'ko_cause': '날짜 형식이 입력 문자열의 길이와 일치하지 않습니다.',
        'en_action': 'Check date format. Verify input data. Use TO_DATE with correct format.',
        'ko_action': '날짜 형식을 확인하세요. 입력 데이터를 확인하세요. 올바른 형식으로 TO_DATE를 사용하세요.',
        'critical': False
    },
    '01839': {
        'name': 'Date not valid for month specified',
        'en_cause': 'The date is invalid for the specified month (e.g., Feb 30).',
        'ko_cause': '지정된 월에 대해 날짜가 유효하지 않습니다 (예: 2월 30일).',
        'en_action': 'Verify the date value. Check for valid day range. Validate input data.',
        'ko_action': '날짜 값을 확인하세요. 유효한 날짜 범위를 확인하세요. 입력 데이터를 검증하세요.',
        'critical': False
    },
    '01841': {
        'name': '4-digit year must be between -4713 and +9999',
        'en_cause': 'The year value is outside the valid range.',
        'ko_cause': '연도 값이 유효한 범위를 벗어났습니다.',
        'en_action': 'Use year between -4713 and 9999. Check input value. Correct date value.',
        'ko_action': '-4713~9999 사이의 연도를 사용하세요. 입력 값을 확인하세요. 날짜 값을 수정하세요.',
        'critical': False
    },
    '01843': {
        'name': 'Not a valid month',
        'en_cause': 'The month value is not valid (must be 1-12).',
        'ko_cause': '월 값이 유효하지 않습니다 (1-12여야 함).',
        'en_action': 'Use month between 1 and 12. Verify month value. Check input format.',
        'ko_action': '1~12 사이의 월을 사용하세요. 월 값을 확인하세요. 입력 형식을 확인하세요.',
        'critical': False
    },
    '02000': {
        'name': 'No rows selected',
        'en_cause': 'A SELECT statement returned no rows.',
        'ko_cause': 'SELECT 문이 행을 반환하지 않았습니다.',
        'en_action': 'Check query conditions. Verify data exists. Modify WHERE clause.',
        'ko_action': '쿼리 조건을 확인하세요. 데이터가 존재하는지 확인하세요. WHERE 절을 수정하세요.',
        'critical': False
    },
    '02014': {
        'name': 'Cannot select FOR UPDATE from view',
        'en_cause': 'FOR UPDATE cannot be used with a view that has multiple base tables.',
        'ko_cause': 'FOR UPDATE를 여러 기본 테이블이 있는 뷰와 함께 사용할 수 없습니다.',
        'en_action': 'Remove FOR UPDATE from view query. Use view with single base table. Query base table directly.',
        'ko_action': '뷰 쿼리에서 FOR UPDATE를 제거하세요. 단일 기본 테이블이 있는 뷰를 사용하세요. 기본 테이블을 직접 쿼리하세요.',
        'critical': False
    },
    '03001': {
        'name': 'Unimplemented feature',
        'en_cause': 'The feature is not yet implemented in this Oracle version.',
        'ko_cause': '이 Oracle 버전에서 아직 구현되지 않은 기능입니다.',
        'en_action': 'Use alternative feature. Upgrade Oracle version. Check documentation for workaround.',
        'ko_action': '대체 기능을 사용하세요. Oracle 버전을 업그레이드하세요. 문서에서 해결 방법을 확인하세요.',
        'critical': False
    },
    '03113': {
        'name': 'End-of-file on communication channel',
        'en_cause': 'The connection to the database was lost unexpectedly.',
        'ko_cause': '데이터베이스와의 연결이 예기치 않게 끊어졌습니다.',
        'en_action': 'Reconnect to database. Check network connection. Check alert log. Restart instance if needed.',
        'ko_action': '데이터베이스에 다시 연결하세요. 네트워크 연결을 확인하세요. 경고 로그를 확인하세요. 필요시 인스턴스를 다시 시작하세요.',
        'critical': False
    },
    '03114': {
        'name': 'Not connected to ORACLE',
        'en_cause': 'The session is not connected to Oracle database.',
        'ko_cause': '세션이 Oracle 데이터베이스에 연결되지 않았습니다.',
        'en_action': 'Establish database connection. Check connection parameters. Verify listener.',
        'ko_action': '데이터베이스 연결을 확립하세요. 연결 매개변수를 확인하세요. 리스너를 확인하세요.',
        'critical': False
    },
    '04054': {
        'name': 'Database link does not exist',
        'en_cause': 'The referenced database link does not exist.',
        'ko_cause': '참조된 데이터베이스 링크가 없습니다.',
        'en_action': 'Create the database link. Verify link name spelling. Check remote database availability.',
        'ko_action': '데이터베이스 링크를 생성하세요. 링크 이름 철자를 확인하세요. 원격 데이터베이스 가용성을 확인하세요.',
        'critical': False
    },
    '04092': {
        'name': 'CREATE OR REPLACE not supported for database links',
        'en_cause': 'Cannot use CREATE OR REPLACE for database links.',
        'ko_cause': '데이터베이스 링크에 CREATE OR REPLACE를 사용할 수 없습니다.',
        'en_action': 'Drop the link first, then create. Use DROP then CREATE syntax.',
        'ko_action': '먼저 링크를 삭제한 다음 생성하세요. DROP 다음 CREATE 문법을 사용하세요.',
        'critical': False
    },
    '06512': {
        'name': 'PL/SQL: Cursor already open',
        'en_cause': 'An attempt was made to open a cursor that is already open.',
        'ko_cause': '이미 열려있는 커서를 열려고 시도했습니다.',
        'en_action': 'Close the cursor before reopening. Check cursor state. Use exception handling.',
        'ko_action': '다시 열기 전에 커서를 닫으세요. 커서 상태를 확인하세요. 예외 처리를 사용하세요.',
        'critical': False
    },
    '06513': {
        'name': 'PL/SQL: Variable Declarations End',
        'en_cause': 'Syntax error in PL/SQL variable declaration section.',
        'ko_cause': 'PL/SQL 변수 선언 섹션의 문법 오류.',
        'en_cause': 'Check variable declaration syntax. Review PL/SQL code. Use correct END keyword.',
        'ko_action': '변수 선언 문법을 확인하세요. PL/SQL 코드를 검토하세요. 올바른 END 키워드를 사용하세요.',
        'critical': False
    }
}

# DB 버전 선택
DB_VERSIONS = ['11g', '12c', '18c', '19c', '21c', '23c', '26i']

# 크리티컬 에러 목록
CRITICAL_ERRORS = {code for code, info in ORACLE_ERRORS.items() if info['critical']}

def extract_ora_errors(text):
    """Alert Log 텍스트에서 ORA- 에러 추출"""
    # ORA-XXXXX 또는 XXXXX (5자리 숫자) 형식 모두 매칭
    pattern = r'(?:ORA-)?(\d{5})(?:[:\s]([^\n]*)?)?'
    matches = re.findall(pattern, text, re.MULTILINE)

    errors = []
    for code, message in matches:
        is_found = code in ORACLE_ERRORS
        error_info = ORACLE_ERRORS.get(code, {
            'name': 'Unknown error',
            'en_cause': 'No information available in local database.',
            'ko_cause': '로컬 데이터베이스에 사용 가능한 정보가 없습니다.',
            'en_action': 'Check Oracle official documentation using the link below.',
            'ko_action': '아래 링크에서 Oracle 공식 문서를 확인하세요.',
            'critical': False
        })

        errors.append({
            'Error Code': f'ORA-{code}',
            'Name': error_info['name'],
            'Message': message.strip() if message else '',
            'Code': code,
            'Critical': code in CRITICAL_ERRORS,
            'Info': error_info,
            'Found': is_found
        })

    return errors

def get_oracle_doc_url(db_version, ora_code):
    """Oracle 공식 문서 링크 생성"""
    # Oracle 문서 검색 URL
    return f"https://docs.oracle.com/search/?q={ora_code}&book=DBERR&library=en%2Ferror-help"

# 제목
st.title("🔍 Oracle Alert Log 분석기")

st.markdown("---")

# DB 버전은 기본으로 설정 (사용자 선택 필요 없음)
db_version = '19c'

# 메인 콘텐츠
st.subheader("📋 Alert Log 입력")
alert_log_text = st.text_area(
    "Oracle Alert Log 내용을 입력하세요 (ORA-로 시작하거나 번호만 입력):",
    height=200,
    placeholder="ORA-01489 또는 01489\nORA-16038: log file corrupted\n00600"
)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    analyze_button = st.button("🔍 분석하기", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ 초기화", use_container_width=True)

if clear_button:
    st.rerun()

# 분석 결과
if analyze_button and alert_log_text.strip():
    errors = extract_ora_errors(alert_log_text)

    if not errors:
        st.warning("⚠️ ORA- 에러를 찾을 수 없습니다.")
    else:
        # 크리티컬 에러 체크
        critical_errors = [e for e in errors if e['Critical']]

        if critical_errors:
            st.markdown(
                f"""
                <div class="critical-alert">
                ⚠️ 크리티컬 에러 발견! ({len(critical_errors)}개)
                <br>즉시 조치가 필요합니다!
                </div>
                """,
                unsafe_allow_html=True
            )

            # 크리티컬 에러 상세 정보
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

                    st.markdown(f"📖 [Oracle 공식 문서 보기]({get_oracle_doc_url(db_version, error['Code'])})")

        # 전체 에러 테이블
        st.markdown("### 📊 발견된 모든 에러 목록")

        # 테이블 데이터 준비
        table_data = []
        for i, error in enumerate(errors, 1):
            table_data.append({
                '순번': i,
                '에러 코드': error['Error Code'],
                '에러명': error['Name'],
                '심각도': '🔴 크리티컬' if error['Critical'] else '🟡 일반',
                '메시지': error['Message'][:50] + '...' if len(error['Message']) > 50 else error['Message']
            })

        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                '순번': st.column_config.NumberColumn(width=60),
                '에러 코드': st.column_config.TextColumn(width=100),
                '에러명': st.column_config.TextColumn(width=150),
                '심각도': st.column_config.TextColumn(width=100),
                '메시지': st.column_config.TextColumn(width=300)
            }
        )

        # 각 에러별 Cause & Action 표시
        st.markdown("### 📋 원인 및 조치 (Cause & Action)")
        for i, error in enumerate(errors, 1):
            with st.container(border=True):
                if error['Found']:
                    st.markdown(f"#### {i}. **ORA-{error['Code']}** - {error['Name']}")
                else:
                    st.markdown(f"#### {i}. **ORA-{error['Code']}** - {error['Name']} ❓ (정보 없음)")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**원인 (Cause)**")
                    st.info(f"🇬🇧 {error['Info']['en_cause']}", icon="📌")
                    st.info(f"🇰🇷 {error['Info']['ko_cause']}", icon="📌")

                with col2:
                    st.markdown("**조치 (Action)**")
                    st.success(f"🇬🇧 {error['Info']['en_action']}", icon="✅")
                    st.success(f"🇰🇷 {error['Info']['ko_action']}", icon="✅")

                if not error['Found']:
                    st.warning(
                        f"⚠️ 이 에러는 로컬 데이터베이스에 없습니다. "
                        f"아래 링크에서 Oracle 공식 문서를 확인해주세요."
                    )

                st.markdown(
                    f"📖 [Oracle 공식 문서에서 ORA-{error['Code']} 검색하기]"
                    f"({get_oracle_doc_url(db_version, error['Code'])})"
                )

        # 에러별 상세 정보
        st.markdown("### 📝 에러 상세 정보")

        for error in errors:
            with st.expander(f"ORA-{error['Code']} - {error['Name']}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📌 원인 (Cause)")
                    st.write(f"🇬🇧 **English:** {error['Info']['en_cause']}")
                    st.write(f"🇰🇷 **한국어:** {error['Info']['ko_cause']}")

                with col2:
                    st.markdown("#### ✅ 조치 (Action)")
                    st.write(f"🇬🇧 **English:** {error['Info']['en_action']}")
                    st.write(f"🇰🇷 **한국어:** {error['Info']['ko_action']}")

                st.markdown(f"📖 [Oracle 공식 문서 보기]({get_oracle_doc_url(db_version, error['Code'])})")

        # 요약 통계
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
    st.error("❌ Alert Log 텍스트를 입력해주세요.")

# 하단 정보
st.markdown("---")
st.markdown("""
### 💡 사용 방법
1. **DB 버전** 선택
2. Oracle Alert Log 내용을 텍스트 박스에 **복사·붙여넣기**
3. **분석하기** 버튼 클릭
4. 발견된 에러와 조치 가이드 확인
5. 필요시 Oracle 공식 문서 링크로 추가 정보 조회

### 🔴 크리티컬 에러
크리티컬 에러는 데이터베이스의 즉각적인 문제를 나타냅니다. 발견되면 빨간색 경고창이 표시되며, 조치 가이드를 따라 신속하게 대응하세요.

**현재 크리티컬 에러**: ORA-01555, ORA-01578, ORA-01650, ORA-01658, ORA-16038, ORA-04031, ORA-30951, ORA-16014, ORA-27056, ORA-00600
""")
