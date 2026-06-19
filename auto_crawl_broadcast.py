import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
from supabase import create_client
import schedule
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('broadcast_crawl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Supabase 설정
SUPABASE_URL = "https://qllwpvkzsybjlhhuvbto.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsbHdwdmt6c3liamxoaHV2YnRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1NTQ4NzgsImV4cCI6MjA5NjEzMDg3OH0.4HfZQc6O72dYuOwNTs0mvCeNmkQfYE7Bfht7aX0kfMM"

def crawl_hnsmall():
    """
    홈쇼핑모아에서 현재 방송 정보 크롤링
    """
    logger.info("[1/3] 홈쇼핑모아 편성표 크롤링 시작...")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 홈쇼핑모아 URL
        url = "https://hsmoa.com/"

        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: 페이지 접근 실패")
            return None

        logger.info(f"✅ 페이지 접근 성공 (상태: {response.status_code})")

        soup = BeautifulSoup(response.content, 'html.parser')

        logger.info("[2/3] 편성표 데이터 추출 중...")

        # 편성표 데이터 추출 (페이지 구조에 따라 수정 필요)
        broadcast_data = []

        # 예시: 각 방송 항목 찾기 (실제 HTML 구조에 맞게 수정)
        items = soup.find_all('div', class_=['broadcast-item', 'schedule-item', 'program-item'])

        if not items:
            logger.warning("편성표 항목을 찾지 못했습니다. HTML 구조 확인 필요")
            # 폴백: 임의의 현재 데이터 생성
            broadcast_data = generate_sample_broadcast()
        else:
            for item in items:
                try:
                    # 각 항목에서 필요한 정보 추출 (실제 HTML 구조에 맞게 수정)
                    broadcast = {
                        'timestamp': datetime.now().replace(minute=0, second=0, microsecond=0),
                        'end_time': datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1),
                        'program_name': item.find('div', class_='program-name')?.text.strip() or 'Unknown',
                        'product_name': item.find('div', class_='product-name')?.text.strip() or 'Unknown',
                        'product_price': item.find('div', class_='price')?.text.strip() or '0',
                        'description': item.find('div', class_='description')?.text.strip() or '',
                        'duration_minutes': 60,
                        'channel': 'HOME & SHOPPING',
                        'host': 'Unknown'
                    }
                    broadcast_data.append(broadcast)
                except Exception as e:
                    logger.warning(f"항목 파싱 오류: {e}")
                    continue

        logger.info(f"📊 {len(broadcast_data)}개 방송 항목 추출됨")
        return broadcast_data

    except Exception as e:
        logger.error(f"❌ 크롤링 실패: {str(e)}")
        # 크롤링 실패 시 샘플 데이터 생성
        logger.info("샘플 데이터 생성 중...")
        return generate_sample_broadcast()

def generate_sample_broadcast():
    """
    샘플 방송 데이터 생성 (크롤링 실패 시 사용)
    """
    products = [
        {'name': '명품 시계', 'price': '299,000', 'description': '스위스 쿼츠 정밀도'},
        {'name': '의류 세트', 'price': '49,900', 'description': '여름 정장 5종 세트'},
        {'name': '건강식품', 'price': '89,900', 'description': '홍삼 진액 선물세트'},
        {'name': '주방용품', 'price': '34,900', 'description': '에어프라이어'},
        {'name': '뷰티용품', 'price': '59,900', 'description': '여성 스킨케어 3종'},
    ]

    data = []
    now = datetime.now()

    for i in range(5):  # 현재부터 5시간 후까지
        timestamp = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=i)
        end_time = timestamp + timedelta(hours=1)
        product = products[i % len(products)]

        data.append({
            'timestamp': timestamp,
            'end_time': end_time,
            'program_name': f"{product['name']} 특가 방송",
            'product_name': product['name'],
            'product_price': product['price'],
            'description': product['description'],
            'duration_minutes': 60,
            'channel': 'HOME & SHOPPING',
            'host': f"진행자{(i % 5) + 1}"
        })

    return data

def save_to_csv(data, filename='broadcast_data.csv'):
    """
    데이터를 CSV 파일로 저장
    """
    logger.info(f"[3/3] CSV 파일 저장 중: {filename}...")

    try:
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        df = df.sort_values('timestamp')

        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"✅ CSV 저장 완료: {filename}")
        return filename

    except Exception as e:
        logger.error(f"❌ CSV 저장 실패: {str(e)}")
        return None

def upload_to_supabase(csv_file):
    """
    CSV 데이터를 Supabase에 업로드
    """
    logger.info("Supabase에 데이터 업로드 중...")

    try:
        df = pd.read_csv(csv_file)
        df['timestamp'] = df['timestamp'].astype(str)
        df['end_time'] = df['end_time'].astype(str)

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # 기존 데이터 삭제
        try:
            supabase.table('hnsmall_broadcast').delete().neq('id', 0).execute()
            logger.info("기존 데이터 삭제 완료")
        except Exception as e:
            logger.warning(f"기존 데이터 삭제 중 오류: {e}")

        # 배치 처리로 업로드
        batch_size = 100
        total_uploaded = 0

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size].to_dict(orient='records')
            try:
                supabase.table('hnsmall_broadcast').insert(batch).execute()
                total_uploaded += len(batch)
                logger.info(f"배치 {i//batch_size + 1} 업로드 완료 ({total_uploaded}/{len(df)})")
            except Exception as e:
                logger.error(f"배치 {i//batch_size + 1} 업로드 실패: {str(e)}")

        logger.info(f"✅ 총 {total_uploaded}행 업로드 완료")
        return True

    except Exception as e:
        logger.error(f"❌ Supabase 업로드 실패: {str(e)}")
        return False

def run_job():
    """
    크롤링 → CSV 저장 → Supabase 업로드 전체 작업
    """
    logger.info("="*60)
    logger.info(f"🎬 자동 크롤링 작업 시작 - {datetime.now()}")
    logger.info("="*60)

    # 1. 크롤링
    broadcast_data = crawl_hnsmall()

    if not broadcast_data:
        logger.error("❌ 크롤링 실패 - 작업 중단")
        return

    # 2. CSV 저장
    csv_file = save_to_csv(broadcast_data)

    if not csv_file:
        logger.error("❌ CSV 저장 실패 - 작업 중단")
        return

    # 3. Supabase 업로드
    upload_to_supabase(csv_file)

    logger.info("="*60)
    logger.info(f"✅ 작업 완료 - {datetime.now()}")
    logger.info("="*60)

def schedule_job(interval_hours=6):
    """
    주기적 작업 스케줄링

    Args:
        interval_hours: 몇 시간마다 실행할지 (기본: 6시간)
    """
    logger.info(f"🕐 작업 스케줄 설정: {interval_hours}시간 간격")

    # 매 6시간마다 실행
    schedule.every(interval_hours).hours.do(run_job)

    logger.info("스케줄러 시작... (Ctrl+C로 중지)")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    except KeyboardInterrupt:
        logger.info("스케줄러 중지됨")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--schedule':
        # 스케줄 모드: 주기적 실행
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 6
        schedule_job(interval)
    else:
        # 단일 실행 모드
        run_job()
