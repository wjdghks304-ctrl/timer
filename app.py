import streamlit as st
import time
import math

# 1. 페이지 기본 설정 (가장 먼저 호출되어야 합니다)
st.set_page_config(
    page_title="나만의 반응형 타이머",
    page_icon="⏱️",
    layout="centered"
)

# 2. 화면 디자인을 위한 CSS 스타일 적용 (반응형 글자 크기, 카드 모양 등)
st.markdown("""
<style>
    /* 타이머 숫자를 보여주는 큰 카드 디자인 */
    .timer-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.1);
        text-align: center;
        margin: 20px auto;
    }
    
    /* 타이머 텍스트 반응형 설정: 화면 크기에 따라 글자 크기가 자동 조절됩니다 (clamp 사용) */
    .timer-text {
        font-size: clamp(4rem, 15vw, 8rem);
        font-weight: 800;
        color: #FF4B4B; /* 밝은 빨간색 */
        line-height: 1.2;
        /* 숫자의 폭을 일정하게 맞춰주어 시간이 바뀔 때 화면이 흔들리지 않게 합니다 */
        font-variant-numeric: tabular-nums; 
    }
</style>
""", unsafe_allow_html=True)


# 3. 상태 저장소 (st.session_state) 초기화
# 프로그램이 다시 실행되어도 데이터가 날아가지 않도록 상태를 저장합니다.
if 'state' not in st.session_state:
    st.session_state.state = 'idle' # 상태 종류: idle(대기), running(실행중), paused(일시정지), finished(종료)
if 'remaining_seconds' not in st.session_state:
    st.session_state.remaining_seconds = 0
if 'total_seconds' not in st.session_state:
    st.session_state.total_seconds = 0
if 'end_time' not in st.session_state:
    st.session_state.end_time = 0.0
if 'balloon_shown' not in st.session_state:
    st.session_state.balloon_shown = False

# 시간 입력 위젯과 연결될 변수
if 'input_minutes' not in st.session_state:
    st.session_state.input_minutes = 0
if 'input_seconds' not in st.session_state:
    st.session_state.input_seconds = 0


# 4. 버튼 클릭 시 실행될 함수들 정의
def set_quick_time(minutes):
    """빠른 시간 설정 버튼을 눌렀을 때 실행되는 함수"""
    st.session_state.input_minutes = minutes
    st.session_state.input_seconds = 0

def start_timer():
    """타이머 시작 함수"""
    total = (st.session_state.input_minutes * 60) + st.session_state.input_seconds
    if total <= 0:
        st.error("0분 0초로는 시작할 수 없습니다. 시간을 설정해 주세요!")
        return
    
    st.session_state.total_seconds = total
    st.session_state.remaining_seconds = total
    # 단순히 1씩 빼는 것이 아니라, 컴퓨터의 실제 시간(monotonic)을 기준으로 종료 시간을 계산합니다.
    st.session_state.end_time = time.monotonic() + total
    st.session_state.state = 'running'
    st.session_state.balloon_shown = False # 풍선 효과 초기화

def pause_timer():
    """타이머 일시정지 함수"""
    st.session_state.state = 'paused'
    # 멈춘 순간의 남은 시간을 정확히 계산하여 저장합니다.
    st.session_state.remaining_seconds = st.session_state.end_time - time.monotonic()

def resume_timer():
    """타이머 계속(재개) 함수"""
    st.session_state.state = 'running'
    # 저장된 남은 시간을 바탕으로 새로운 종료 시간을 다시 계산합니다.
    st.session_state.end_time = time.monotonic() + st.session_state.remaining_seconds

def reset_timer():
    """타이머 초기화 함수"""
    st.session_state.state = 'idle'
    st.session_state.remaining_seconds = 0
    st.session_state.balloon_shown = False


# 5. 메인 UI 구성
st.title("⏱️ 나만의 반응형 타이머")

# 타이머가 실행 중이거나 일시정지 상태일 때는 시간 설정을 건드릴 수 없도록 막습니다(비활성화).
is_disabled = st.session_state.state in ['running', 'paused']

st.markdown("### 1️⃣ 시간 설정")
# 모바일에서도 보기 좋게 4칸으로 나누어 빠른 설정 버튼을 배치합니다.
col1, col2, col3, col4 = st.columns(4)
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

# 직접 입력하는 부분
col_m, col_s = st.columns(2)
with col_m:
    # key 매개변수를 이용해 session_state 변수와 직접 연결합니다. 음수는 입력 불가(min_value=0)
    st.number_input("분 (Minutes)", min_value=0, max_value=999, step=1, key="input_minutes", disabled=is_disabled)
with col_s:
    st.number_input("초 (Seconds)", min_value=0, max_value=59, step=1, key="input_seconds", disabled=is_disabled)


st.markdown("### 2️⃣ 타이머 조작")
# 시작, 일시정지, 계속, 초기화 버튼 배치
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    # 현재 상태에 따라 보여주는 버튼이 다릅니다.
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
    # 초기화 버튼은 대기(idle) 상태일 때만 비활성화합니다.
    if st.button("🔄 초기화", use_container_width=True, disabled=(st.session_state.state == 'idle')):
        reset_timer()


st.markdown("### 3️⃣ 남은 시간")

# 6. 부분 새로고침(st.fragment) 설정
# run_every="1s"를 설정하여 1초마다 이 함수 안의 화면만 깜빡임 없이 새로고침합니다.
@st.fragment(run_every="1s")
def display_timer_fragment():
    # 실행 중일 때만 남은 시간을 계산합니다.
    if st.session_state.state == 'running':
        now = time.monotonic()
        left_time = st.session_state.end_time - now
        
        # 시간이 다 되었을 때
        if left_time <= 0:
            st.session_state.remaining_seconds = 0
            st.session_state.state = 'finished'
            st.rerun() # 전체 화면을 한 번 새로고침하여 완료 상태를 확실히 반영합니다.
        else:
            st.session_state.remaining_seconds = left_time

    # 남은 시간을 분과 초로 나눕니다 (math.ceil을 써서 0.1초라도 남아있으면 1초로 표시되게 올림 처리합니다)
    display_sec = max(0, math.ceil(st.session_state.remaining_seconds))
    mins = display_sec // 60
    secs = display_sec % 60

    # HTML과 CSS를 결합하여 화면 중앙에 큰 글씨로 시간을 표시합니다. (MM:SS 형태)
    html_code = f"""
    <div class="timer-card">
        <div class="timer-text">{mins:02d}:{secs:02d}</div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

    # 진행률 막대(Progress bar) 표시
    if st.session_state.total_seconds > 0:
        # 진행률은 0.0 에서 1.0 사이의 값이어야 합니다.
        progress = st.session_state.remaining_seconds / st.session_state.total_seconds
        progress = max(0.0, min(1.0, progress)) # 오류 방지를 위해 범위 제한
        st.progress(progress)

# 위에서 정의한 화면 그리기 함수를 실행합니다.
display_timer_fragment()


# 7. 종료 시 시각적 효과 (풍선)
if st.session_state.state == 'finished' and not st.session_state.balloon_shown:
    st.success("타이머가 종료되었습니다! 수고하셨습니다. 👏")
    st.balloons() # 화면에 풍선이 날아가는 효과
    st.session_state.balloon_shown = True # 풍선이 한 번만 나오도록 상태 변경
