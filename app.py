import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import calendar
from supabase import create_client

st.set_page_config(
    page_title="DB 모니터링",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');

    * {
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    .main {
        background-color: #f4f7fb;
    }

    .block-container {
        background-color: #f4f7fb;
        padding: 2.5rem;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #1E5FAD;
        font-weight: 700;
    }

    .stMetric {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        border-left: 6px solid #1E5FAD;
        box-shadow: 0 2px 8px rgba(30, 95, 173, 0.12);
    }

    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        color: #1E5FAD !important;
    }

    [data-testid="stMetricLabel"] {
        color: #555 !important;
        font-size: 14px !important;
    }

    .stDataFrame {
        background-color: white;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
    }

    [data-testid="collapsedControl"] span,
    button[data-testid="collapsedControl"] {
        font-family: 'Material Symbols Outlined' !important;
        font-size: 20px !important;
    }

    [data-testid="selectbox"] {
        font-size: 12px !important;
    }

    [data-testid="selectbox"] > div > div > select {
        font-size: 12px !important;
        min-width: 75px !important;
    }

    div[data-baseweb="select"] {
        font-size: 12px !important;
        min-width: 75px !important;
    }

    div[data-baseweb="select"] span {
        font-size: 12px !important;
    }

    div[data-baseweb="select"] input {
        font-size: 12px !important;
    }

    [data-testid="stSelectbox"] > div {
        min-width: 85px !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f8fafb;
    }

    hr {
        border-color: #dce8f7 !important;
    }

    button[data-testid="collapsedControl"] {
        position: relative !important;
        background: transparent !important;
        border: none !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        overflow: hidden !important;
        text-indent: -9999px !important;
        line-height: 0 !important;
        font-size: 0 !important;
        color: transparent !important;
    }

    button[data-testid="collapsedControl"] * {
        font-size: 0 !important;
        color: transparent !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        display: none !important;
    }

    button[data-testid="collapsedControl"]::after {
        content: '▶';
        text-indent: 0 !important;
        line-height: normal !important;
        font-size: 20px !important;
        color: #1E5FAD !important;
        font-weight: bold !important;
        visibility: visible !important;
        display: block !important;
        position: absolute !important;
        width: auto !important;
        height: auto !important;
    }

    button[data-testid="collapsedControl"][aria-expanded="true"]::after {
        content: '◀';
    }

    button[data-testid="collapsedControl"]:hover {
        background: rgba(30, 95, 173, 0.1) !important;
        border-radius: 4px !important;
    }

    .stButton > button[kind="primary"] {
        background-color: #1E5FAD !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(30, 95, 173, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #164d8f !important;
        box-shadow: 0 3px 10px rgba(30, 95, 173, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Supabase에서 DBA 모니터링 데이터 로드"""
    try:
        # Streamlit Secrets에서 Supabase 정보 로드
        supabase_url = st.secrets["supabase_url"]
        supabase_key = st.secrets["supabase_key"]

        # Supabase 클라이언트 초기화
        supabase = create_client(supabase_url, supabase_key)

        # dba_monitoring 테이블에서 모든 데이터 조회
        response = supabase.table("dba_monitoring").select("*").execute()

        if not response.data:
            st.error("❌ Supabase에서 데이터를 로드할 수 없습니다.")
            return pd.DataFrame()

        # DataFrame으로 변환
        df = pd.DataFrame(response.data)

        # 컬럼명 매핑 (Supabase 컬럼을 기존 CSV 형식으로 변환)
        df.rename(columns={
            'db_name': 'DB명',
            'cpu_usage': 'CPU사용율(%)',
            'active_sessions': 'Active Session 수',
            'lock_sessions': 'Lock Session 수',
            'alertlog_count': 'AlertLog Count'
        }, inplace=True)

        # timestamp를 datetime으로 변환
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        return df

    except KeyError:
        st.error("❌ Streamlit Secrets에 'supabase_url'과 'supabase_key'가 필요합니다.")
        st.info("""
        `.streamlit/secrets.toml` 파일을 생성하고 다음을 추가하세요:
        ```
        supabase_url = "https://qllwpvkzsybjlhhuvbto.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        ```
        """)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류: {str(e)}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

data_min = df['timestamp'].min()
data_max = df['timestamp'].max()
db_options = sorted(df['DB명'].unique())

if 'applied_start' not in st.session_state:
    st.session_state.applied_start = data_min
    st.session_state.applied_end = data_max
    st.session_state.applied_dbs = list(db_options)

st.title('📊 DB 모니터링')
st.markdown('<p style="color: #7f8c8d; font-size: 14px;">데이터베이스 실시간 모니터링 대시보드 (Supabase 연동)</p>', unsafe_allow_html=True)
st.markdown('---')

with st.sidebar:
    st.title('🔍 검색 기간')
    st.markdown('---')

    st.write('**모니터링 DB 선택**')
    cols = st.columns(len(db_options))

    selected_dbs = []
    for idx, db_name in enumerate(db_options):
        with cols[idx]:
            if st.checkbox(db_name, value=True, key=f'db_{db_name}'):
                selected_dbs.append(db_name)

    st.markdown('---')

    BASE_YEAR = 2026
    year_options = list(range(BASE_YEAR - 5, BASE_YEAR + 6))

    # 시작 시간 선택
    st.write('**시작 시간**')
    start_col1, start_col2, start_col3, start_col4, start_col5 = st.columns(5)

    with start_col1:
        start_year = st.selectbox('년', year_options, index=year_options.index(data_min.year), key='start_year')
    with start_col2:
        start_month = st.selectbox('월', list(range(1, 13)), index=data_min.month - 1, key='start_month')
    with start_col3:
        max_day_start = calendar.monthrange(start_year, start_month)[1]
        day_options_start = list(range(1, max_day_start + 1))
        start_day = st.selectbox('일', day_options_start, index=min(data_min.day, max_day_start) - 1, key='start_day')
    with start_col4:
        start_hour = st.selectbox('시', list(range(0, 24)), index=data_min.hour, key='start_hour')
    with start_col5:
        start_minute = st.selectbox('분', list(range(0, 60)), index=data_min.minute, key='start_minute')

    start_time = pd.Timestamp(year=start_year, month=start_month, day=start_day, hour=start_hour, minute=start_minute)

    st.markdown('')

    # 종료 시간 선택
    st.write('**종료 시간**')
    end_col1, end_col2, end_col3, end_col4, end_col5 = st.columns(5)

    with end_col1:
        end_year = st.selectbox('년', year_options, index=year_options.index(data_max.year), key='end_year')
    with end_col2:
        end_month = st.selectbox('월', list(range(1, 13)), index=data_max.month - 1, key='end_month')
    with end_col3:
        max_day_end = calendar.monthrange(end_year, end_month)[1]
        day_options_end = list(range(1, max_day_end + 1))
        end_day = st.selectbox('일', day_options_end, index=min(data_max.day, max_day_end) - 1, key='end_day')
    with end_col4:
        end_hour = st.selectbox('시', list(range(0, 24)), index=data_max.hour, key='end_hour')
    with end_col5:
        end_minute = st.selectbox('분', list(range(0, 60)), index=data_max.minute, key='end_minute')

    end_time = pd.Timestamp(year=end_year, month=end_month, day=end_day, hour=end_hour, minute=end_minute)

    st.markdown('')
    if st.button('🔍 조회', type='primary', use_container_width=True):
        st.session_state.applied_start = start_time
        st.session_state.applied_end = end_time
        st.session_state.applied_dbs = selected_dbs if selected_dbs else list(db_options)

filtered_df = df[
    (df['DB명'].isin(st.session_state.applied_dbs)) &
    (df['timestamp'] >= st.session_state.applied_start) &
    (df['timestamp'] <= st.session_state.applied_end)
].copy()

if len(filtered_df) == 0:
    st.warning('선택한 기간과 DB에 해당하는 데이터가 없습니다.')
    st.stop()

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_cpu = filtered_df['CPU사용율(%)'].mean()
    st.metric(
        '평균 CPU 사용률',
        f'{avg_cpu:.1f}%',
        delta=f'{avg_cpu - filtered_df["CPU사용율(%)"].iloc[0]:.1f}%' if len(filtered_df) > 0 else None
    )

with col2:
    avg_session = filtered_df['Active Session 수'].mean()
    st.metric(
        '평균 Active Session',
        f'{avg_session:.0f}',
        delta=None
    )

with col3:
    max_lock = filtered_df['Lock Session 수'].max()
    st.metric(
        '최대 Lock Session',
        f'{max_lock}',
        delta=None
    )

with col4:
    total_alert = filtered_df['AlertLog Count'].sum()
    st.metric(
        '총 Alert 로그',
        f'{int(total_alert)}',
        delta=None
    )

st.markdown('---')

st.subheader('📊 시각화 대시보드')

col1, col2 = st.columns(2)

# 날짜 범위 추출
date_range = f"{filtered_df['timestamp'].min().strftime('%Y/%m/%d')} ~ {filtered_df['timestamp'].max().strftime('%Y/%m/%d')}"

with col1:
    fig_cpu = go.Figure()
    for db_name in st.session_state.applied_dbs:
        db_data = filtered_df[filtered_df['DB명'] == db_name].sort_values('timestamp')
        fig_cpu.add_trace(go.Scatter(
            x=db_data['timestamp'],
            y=db_data['CPU사용율(%)'],
            mode='lines',
            name=db_name,
            line=dict(width=2),
            hovertemplate='<b>%{fullData.name}</b><br>%{x|%m/%d %H:%M}<br>CPU: %{y:.1f}%<extra></extra>'
        ))

    fig_cpu.update_layout(
        title='CPU 사용률 추이',
        xaxis_title='',
        yaxis_title='사용률 (%)',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
        margin=dict(l=50, r=30, t=50, b=30),
        xaxis=dict(tickformat='%H:%M')
    )
    fig_cpu.add_annotation(
        text=date_range,
        xref='paper', yref='paper',
        x=0.99, y=0.95,
        showarrow=False,
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='#ccc',
        borderwidth=1,
        borderpad=4,
        font=dict(size=11, color='#555')
    )
    st.plotly_chart(fig_cpu, use_container_width=True)

with col2:
    fig_session = go.Figure()
    for db_name in st.session_state.applied_dbs:
        db_data = filtered_df[filtered_df['DB명'] == db_name].sort_values('timestamp')
        fig_session.add_trace(go.Scatter(
            x=db_data['timestamp'],
            y=db_data['Active Session 수'],
            mode='lines',
            name=db_name,
            line=dict(width=2),
            hovertemplate='<b>%{fullData.name}</b><br>%{x|%m/%d %H:%M}<br>세션: %{y:.0f}<extra></extra>'
        ))

    fig_session.update_layout(
        title='Active Session 수 추이',
        xaxis_title='',
        yaxis_title='세션 수',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
        margin=dict(l=50, r=30, t=50, b=30),
        xaxis=dict(tickformat='%H:%M')
    )
    fig_session.add_annotation(
        text=date_range,
        xref='paper', yref='paper',
        x=0.99, y=0.95,
        showarrow=False,
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='#ccc',
        borderwidth=1,
        borderpad=4,
        font=dict(size=11, color='#555')
    )
    st.plotly_chart(fig_session, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig_lock = go.Figure()
    for db_name in st.session_state.applied_dbs:
        db_data = filtered_df[filtered_df['DB명'] == db_name].sort_values('timestamp')
        fig_lock.add_trace(go.Scatter(
            x=db_data['timestamp'],
            y=db_data['Lock Session 수'],
            mode='lines+markers',
            name=db_name,
            line=dict(width=2),
            marker=dict(size=4),
            hovertemplate='<b>%{fullData.name}</b><br>%{x|%m/%d %H:%M}<br>Lock: %{y:.0f}<extra></extra>'
        ))

    fig_lock.update_layout(
        title='Lock Session 수 추이',
        xaxis_title='',
        yaxis_title='세션 수',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
        margin=dict(l=50, r=30, t=50, b=30),
        xaxis=dict(tickformat='%H:%M')
    )
    fig_lock.add_annotation(
        text=date_range,
        xref='paper', yref='paper',
        x=0.99, y=0.95,
        showarrow=False,
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='#ccc',
        borderwidth=1,
        borderpad=4,
        font=dict(size=11, color='#555')
    )
    st.plotly_chart(fig_lock, use_container_width=True)

with col4:
    fig_alert = go.Figure()
    for db_name in st.session_state.applied_dbs:
        db_data = filtered_df[filtered_df['DB명'] == db_name].sort_values('timestamp')
        fig_alert.add_trace(go.Scatter(
            x=db_data['timestamp'],
            y=db_data['AlertLog Count'],
            mode='lines+markers',
            name=db_name,
            line=dict(width=2),
            marker=dict(size=4),
            hovertemplate='<b>%{fullData.name}</b><br>%{x|%m/%d %H:%M}<br>Alert: %{y:.0f}<extra></extra>'
        ))

    fig_alert.update_layout(
        title='Alert 로그 개수 추이',
        xaxis_title='',
        yaxis_title='로그 개수',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
        margin=dict(l=50, r=30, t=50, b=30),
        xaxis=dict(tickformat='%H:%M')
    )
    fig_alert.add_annotation(
        text=date_range,
        xref='paper', yref='paper',
        x=0.99, y=0.95,
        showarrow=False,
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='#ccc',
        borderwidth=1,
        borderpad=4,
        font=dict(size=11, color='#555')
    )
    st.plotly_chart(fig_alert, use_container_width=True)

st.markdown('---')
st.subheader('📋 상세 데이터')

display_cols = ['timestamp', 'DB명', 'CPU사용율(%)', 'Active Session 수', 'Lock Session 수', 'AlertLog Count']
display_df = filtered_df[display_cols].copy()
display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
display_df = display_df.sort_values('timestamp', ascending=False).reset_index(drop=True)

st.dataframe(display_df, use_container_width=True, hide_index=True)

col1, col2 = st.columns([2, 1])
with col2:
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label='📥 CSV 다운로드',
        data=csv,
        file_name=f'db_monitoring_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

st.markdown('---')
st.caption('🔧 © 2026 홈앤쇼핑 DB 모니터링 시스템 (Supabase 연동)')
