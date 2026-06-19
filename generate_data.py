import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from supabase import create_client
import httpx

# 날짜 범위 설정
start_date = pd.Timestamp('2026-06-01 00:00:00')
end_date = pd.Timestamp('2026-06-15 23:59:00')

# 30분 간격으로 타임스탐프 생성
timestamps = pd.date_range(start_date, end_date, freq='30min')

# DB 목록
dbs = ['PROD_DB', 'DEV_DB', 'TEST_DB']

# 데이터 생성
data = []
np.random.seed(42)

for timestamp in timestamps:
    for db in dbs:
        # DB별로 다른 패턴의 가상 데이터 생성
        if db == 'PROD_DB':
            cpu = np.random.randint(35, 75)
            sessions = np.random.randint(100, 300)
            locks = np.random.randint(0, 15)
            alerts = np.random.randint(10, 40)
        elif db == 'DEV_DB':
            cpu = np.random.randint(10, 40)
            sessions = np.random.randint(30, 100)
            locks = np.random.randint(0, 5)
            alerts = np.random.randint(0, 10)
        else:  # TEST_DB
            cpu = np.random.randint(5, 35)
            sessions = np.random.randint(40, 120)
            locks = np.random.randint(0, 8)
            alerts = np.random.randint(0, 15)

        data.append({
            'timestamp': timestamp,
            'db_name': db,
            'cpu_usage': cpu,
            'active_sessions': sessions,
            'lock_sessions': locks,
            'alertlog_count': alerts
        })

# DataFrame 생성
df = pd.DataFrame(data)

# CSV 파일로 저장
df.to_csv('dba_monitoring.csv', index=False)
print("[1/3] CSV file saved")

# Supabase 연결
supabase_url = "https://qllwpvkzsybjlhhuvbto.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsbHdwdmt6c3liamxoaHV2YnRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1NTQ4NzgsImV4cCI6MjA5NjEzMDg3OH0.4HfZQc6O72dYuOwNTs0mvCeNmkQfYE7Bfht7aX0kfMM"

import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

supabase = create_client(supabase_url, supabase_key)

# Supabase 테이블의 기존 데이터 삭제
try:
    supabase.table('dba_monitoring').delete().neq('id', 0).execute()
    print("[2/3] Supabase old data deleted")
except Exception as e:
    print(f"Warning: Could not delete old data: {str(e)}")

# timestamp를 문자열로 변환
supabase_df = df.copy()
supabase_df['timestamp'] = supabase_df['timestamp'].astype(str)

# Supabase에 데이터 삽입 (배치 처리)
batch_size = 100
for i in range(0, len(supabase_df), batch_size):
    batch = supabase_df.iloc[i:i+batch_size].to_dict(orient='records')
    try:
        supabase.table('dba_monitoring').insert(batch).execute()
    except Exception as e:
        print(f"Error inserting batch {i//batch_size + 1}: {str(e)}")

print("[3/3] Supabase updated")
print("")
print("Complete!")
print(f"Data range: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
print(f"Total rows: {len(df):,}")
print(f"DBs: {', '.join(df['db_name'].unique())}")
