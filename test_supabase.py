import pandas as pd
from supabase import create_client
import ssl
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Supabase 연결 정보
supabase_url = "https://qllwpvkzsybjlhhuvbto.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsbHdwdmt6c3liamxoaHV2YnRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1NTQ4NzgsImV4cCI6MjA5NjEzMDg3OH0.4HfZQc6O72dYuOwNTs0mvCeNmkQfYE7Bfht7aX0kfMM"

supabase = create_client(supabase_url, supabase_key)

print("=" * 60)
print("[1] dba_monitoring 테이블 테스트")
print("=" * 60)

try:
    response = supabase.table('dba_monitoring').select('*').range(0, 0).execute()
    print(f"[OK] 응답 상태: 성공")
    print(f"[INFO] 행 개수: {len(response.data)}")
    if response.data:
        print(f"[DATA] 첫 번째 행:")
        for key, value in response.data[0].items():
            print(f"   {key}: {value}")
    else:
        print("[ERROR] 데이터 없음")
except Exception as e:
    print(f"[ERROR] 오류: {str(e)}")

print("\n" + "=" * 60)
print("[2] hnsmall_broadcast 테이블 테스트")
print("=" * 60)

try:
    response = supabase.table('hnsmall_broadcast').select('*').range(0, 0).execute()
    print(f"[OK] 응답 상태: 성공")
    print(f"[INFO] 행 개수: {len(response.data)}")
    if response.data:
        print(f"[DATA] 첫 번째 행:")
        for key, value in response.data[0].items():
            print(f"   {key}: {value}")
    else:
        print("[ERROR] 데이터 없음")
except Exception as e:
    print(f"[ERROR] 오류: {str(e)}")

print("\n" + "=" * 60)
print("[3] hnsmall_broadcast 테이블 전체 개수 조회")
print("=" * 60)

try:
    response = supabase.table('hnsmall_broadcast').select('id', count='exact').execute()
    print(f"[OK] 전체 행 개수: {response.count if hasattr(response, 'count') else 'N/A'}")
except Exception as e:
    print(f"[ERROR] 오류: {str(e)}")

print("\n" + "=" * 60)
print("[4] dba_monitoring 테이블 전체 개수 조회")
print("=" * 60)

try:
    response = supabase.table('dba_monitoring').select('id', count='exact').execute()
    print(f"[OK] 전체 행 개수: {response.count if hasattr(response, 'count') else 'N/A'}")
except Exception as e:
    print(f"[ERROR] 오류: {str(e)}")
