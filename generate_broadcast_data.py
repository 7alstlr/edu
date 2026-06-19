import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 샘플 방송 데이터 생성
def generate_broadcast_data():
    """
    홈앤쇼핑 편성표 샘플 데이터 생성
    """

    # 날짜 범위
    start_date = pd.Timestamp('2026-06-01 00:00:00')
    end_date = pd.Timestamp('2026-06-15 23:00:00')

    # 1시간 단위로 타임스탐프 생성
    timestamps = pd.date_range(start_date, end_date, freq='h')

    # 샘플 상품 (현실적인 홈쇼핑 상품들)
    products = [
        {'name': '명품 시계', 'price': '299,000', 'description': '스위스 쿼츠 정밀도'},
        {'name': '의류 세트', 'price': '49,900', 'description': '여름 정장 5종 세트'},
        {'name': '건강식품', 'price': '89,900', 'description': '홍삼 진액 선물세트'},
        {'name': '주방용품', 'price': '34,900', 'description': '에어프라이어'},
        {'name': '뷰티용품', 'price': '59,900', 'description': '여성 스킨케어 3종'},
        {'name': '침구류', 'price': '79,900', 'description': '여름 쿨 침구세트'},
        {'name': '전자제품', 'price': '199,000', 'description': '무선 청소기'},
        {'name': '신발', 'price': '69,900', 'description': '운동화 3종 모음'},
        {'name': '가방', 'price': '99,900', 'description': '여행용 캐리어'},
        {'name': '악세사리', 'price': '19,900', 'description': '귀금속 목걸이'},
    ]

    # 데이터 생성
    data = []
    np.random.seed(42)

    for timestamp in timestamps:
        # 매 시간마다 상품 정보 추가
        product = products[timestamp.hour % len(products)]

        end_time = timestamp + pd.Timedelta(hours=1)
        data.append({
            'timestamp': timestamp,
            'end_time': end_time,
            'program_name': f"{product['name']} 특가 방송",
            'product_name': product['name'],
            'product_price': product['price'],
            'description': product['description'],
            'duration_minutes': 60,
            'channel': 'HOME & SHOPPING',
            'host': f"진행자{(timestamp.hour % 5) + 1}"
        })

    # DataFrame 생성
    df = pd.DataFrame(data)

    # CSV 저장
    df.to_csv('hnsmall_broadcast_sample.csv', index=False)

    print("Complete!")
    print(f"Data range: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
    print(f"Total broadcast hours: {len(df)}")
    print(f"Product types: {df['product_name'].nunique()}")
    print(f"\nFirst 5 rows:")
    print(df.head())

    return df

if __name__ == "__main__":
    print("홈앤쇼핑 편성표 샘플 데이터 생성\n")
    generate_broadcast_data()
