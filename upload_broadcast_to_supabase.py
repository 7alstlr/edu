import pandas as pd
from supabase import create_client
import httpx

# 방송 데이터를 Supabase에 업로드
def upload_broadcast_to_supabase():
    """
    생성한 방송 데이터를 Supabase에 업로드
    """
    try:
        print("[1/4] CSV 파일 읽기...")

        # CSV 파일 읽기
        df = pd.read_csv('hnsmall_broadcast_sample.csv')
        print(f"  로드된 행: {len(df)}")

        print("[2/4] Supabase 연결...")

        # Supabase 연결 (SSL 검증 비활성화)
        supabase_url = "https://qllwpvkzsybjlhhuvbto.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsbHdwdmt6c3liamxoaHV2YnRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1NTQ4NzgsImV4cCI6MjA5NjEzMDg3OH0.4HfZQc6O72dYuOwNTs0mvCeNmkQfYE7Bfht7aX0kfMM"

        supabase = create_client(supabase_url, supabase_key)

        print("[3/4] 기존 데이터 삭제...")

        # 기존 데이터 삭제
        try:
            supabase.table('hnsmall_broadcast').delete().neq('id', 0).execute()
            print("  기존 데이터 삭제 완료")
        except Exception as e:
            print(f"  테이블 없음 (새로 생성예정): {str(e)[:50]}")

        print("[4/4] 데이터 업로드 중...")

        # timestamp를 문자열로 변환
        df['timestamp'] = df['timestamp'].astype(str)

        # 배치 처리 (100개씩)
        batch_size = 100
        total_inserted = 0

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size].to_dict(orient='records')
            try:
                response = supabase.table('hnsmall_broadcast').insert(batch).execute()
                total_inserted += len(batch)
                print(f"  [{i//batch_size + 1}] {total_inserted}/{len(df)} 업로드됨")
            except Exception as e:
                print(f"  ERROR batch {i//batch_size + 1}: {str(e)[:100]}")

        print("\nComplete!")
        print(f"Total rows uploaded: {total_inserted}")

    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    print("방송 데이터 Supabase 업로드\n")
    upload_broadcast_to_supabase()
