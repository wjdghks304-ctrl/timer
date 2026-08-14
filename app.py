import streamlit as st
import time
import math

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="나만의 반응형 타이머",
    page_icon="🌊", 
    layout="centered"
)

# 2. 화면 디자인을 위한 CSS 스타일 적용
st.markdown("""
<style>
    .timer-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0px 8px 16px rgba(30, 144, 255, 0.15); /* 푸른빛 그림자 */
        text-align: center;
        margin: 20px auto;
    }
    
    .timer-text {
        font-size: clamp(4rem, 15vw, 8rem);
        font-weight: 800;
        color: #1E90FF; /* 🔵 시원한 파란색 */
        line-height: 1.2;
        font-variant-numeric: tabular-nums; 
    }
</style>
""", unsafe_allow_html=True)

# 3. 상태 저장소 초기화
if 'state' not in st.session_state:
    st.session_state.state = 'idle'
if 'remaining_seconds' not in st.session_state:
    st.session_state.remaining_seconds = 0
if 'total_seconds' not in st.session_state:
    st.session_state.total_seconds = 0
if 'end_time' not in st.session_state:
    st.session_state.end_time = 0.0
if 'balloon_shown' not in st.session_state:
    st.session_state.balloon_shown = False
if 'input_minutes' not in st.session_state:
    st.session_state.input_minutes = 0
if 'input_seconds' not in st.session_state:
    st.session_state.input_seconds = 0

# 4. 버튼 클릭 시 실행될 함수들
def set_quick_time(minutes):
    st.session_state.input_minutes = minutes
    st.session_state.input_seconds = 0

def start_timer():
    total = (st.session_state.input_minutes * 60) + st.session_state.input_seconds
    if total <= 0:
        st.error("0분 0초로는 시작할 수 없습니다. 시간을 설정해 주세요!")
        return
    st.session_state.total_seconds = total
    st.session_state.remaining_seconds = total
    st.session_state.end_time = time.monotonic() + total
    st.session_state.state = 'running'
    st.session_state.balloon_shown = False

def pause_timer():
    st.session_state.state = 'paused'
    st.session_state.remaining_seconds = st.session_state.end_time - time.monotonic()

def resume_timer():
    st.session_state.state = 'running'
    st.session_state.end_time = time.monotonic() + st.session_state.remaining_seconds

def reset_timer():
    st.session_state.state = 'idle'
    st.session_state.remaining_seconds = 0
    st.session_state.balloon_shown = False

# 5. 메인 UI 구성
st.title("🌊 나만의 반응형 타이머")

is_disabled = st.session_state.state in ['running', 'paused']

st.markdown("### 1️⃣ 시간 설정")
# 💡 화면을 5칸으로 나누어 30분 버튼이 들어갈 자리를 마련합니다!
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("1분", use_container_width=True, disabled=is_disabled):
        set_quick_time(1)
with col2:
    if st.button("3분", use_container_width=True, disabled=is_disabled):
        set_quick_time(3)
with col3:
    if st.button("5분", use_container_width=True, disabled=is_disabled):
        set_quick_time(5)
with col4:
    if st.button("10분", use_container_width=True, disabled=is_disabled):
        set_quick_time(10)
with col5:
    # 💡 30분 버튼이 추가된 부분입니다.
    if st.button("30분", use_container_width=True, disabled=is_disabled):
        set_quick_time(30)

col_m, col_s = st.columns(2)
with col_m:
    st.number_input("분 (Minutes)", min_value=0, max_value=999, step=1, key="input_minutes", disabled=is_disabled)
with col_s:
    st.number_input("초 (Seconds)", min_value=0, max_value=59, step=1, key="input_seconds", disabled=is_disabled)

st.markdown("### 2️⃣ 타이머 조작")
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.session_state.state == 'idle' or st.session_state.state == 'finished':
        if st.button("▶️ 시작", use_container_width=True, type="primary"):
            start_timer()
    elif st.session_state.state == 'running':
        if st.button("⏸️ 일시정지", use_container_width=True):
            pause_timer()
    elif st.session_state.state == 'paused':
        if st.button("▶️ 계속", use_container_width=True, type="primary"):
            resume_timer()

with btn_col2:
    if st.button("🔄 초기화", use_container_width=True, disabled=(st.session_state.state == 'idle')):
        reset_timer()

st.markdown("### 3️⃣ 남은 시간")

# 6. 부분 새로고침(st.fragment) 설정
@st.fragment(run_every="1s")
def display_timer_fragment():
    if st.session_state.state == 'running':
        now = time.monotonic()
        left_time = st.session_state.end_time - now
        
        if left_time <= 0:
            st.session_state.remaining_seconds = 0
            st.session_state.state = 'finished'
            st.rerun()
        else:
            st.session_state.remaining_seconds = left_time

    display_sec = max(0, math.ceil(st.session_state.remaining_seconds))
    mins = display_sec // 60
    secs = display_sec % 60

    html_code = f"""
    <div class="timer-card">
        <div class="timer-text">{mins:02d}:{secs:02d}</div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

    if st.session_state.total_seconds > 0:
        progress = st.session_state.remaining_seconds / st.session_state.total_seconds
        progress = max(0.0, min(1.0, progress))
        st.progress(progress)

display_timer_fragment()

# 7. 종료 시 시각적 효과
if st.session_state.state == 'finished' and not st.session_state.balloon_shown:
    st.success("타이머가 종료되었습니다! 수고하셨습니다. 👏")
    st.snow() # 파란 테마에 어울리는 눈 내림 효과
    st.session_state.balloon_shown = True
