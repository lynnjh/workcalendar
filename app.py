import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import json
import os

# --- 0. 데이터 저장 및 불러오기 함수 (데이터 유지용) ---
DB_FILE = "tasks_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(tasks):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# --- 1. 페이지 설정 및 GS25 BI 디자인 적용 ---
st.set_page_config(page_title="GS25 상생협력팀 업무달력", layout="wide")

# GS25 신규 BI 컬러 반영 (Dynamic Blue: #0076BE)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .css-1d391kg { background-color: #F8FAFC; } /* 사이드바 배경 */
    h1, h2, h3 { color: #0076BE !important; font-family: 'Pretendard', sans-serif; }
    .stButton>button { 
        background-color: #0076BE; color: white; border-radius: 8px; 
        border: none; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #005A92; color: #DAFFDE; }
    /* 달력 칸 디자인 */
    .calendar-box {
        border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px;
        min-height: 130px; background-color: #FFFFFF; transition: 0.2s;
    }
    .calendar-box:hover { border-color: #0076BE; box-shadow: 0 4px 12px rgba(0,118,190,0.1); }
    .task-item {
        padding: 5px 8px; border-radius: 5px; margin-bottom: 5px;
        font-size: 12px; font-weight: 500; border-left: 4px solid rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 상태 관리 (내비게이션 오류 수정) ---
if "tasks" not in st.session_state:
    st.session_state.tasks = load_data()

# 달력 이동 로직 최적화 (오류 방지)
if "cal_year" not in st.session_state:
    st.session_state.cal_year = datetime.now().year
if "cal_month" not in st.session_state:
    st.session_state.cal_month = datetime.now().month

# --- 3. 사이드바: 사용자 인증 및 업무 입력 ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/GS25_logo.svg/512px-GS25_logo.svg.png", width=150)
    st.title("상생협력팀 업무관리")
    
    # 사용자 이름 입력 (누구나 본인 이름으로 작성 가능)
    user_name = st.text_input("👤 본인 이름을 적어주세요", placeholder="이름을 입력해야 등록 가능")
    
    st.divider()
    
    st.subheader("📝 신규 업무 등록")
    new_task = st.text_input("업무 내용을 적어주세요")
    # 색상 선택 기능 추가
    task_color = st.color_picker("달력 표시 색상 선택", "#0076BE")
    task_date = st.date_input("날짜 선택", datetime.now())
    
    if st.button("업무 저장하기", use_container_width=True):
        if not user_name:
            st.error("이름을 먼저 입력해주세요!")
        elif not new_task:
            st.error("업무 내용을 입력해주세요!")
        else:
            new_item = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                "date": task_date.strftime("%Y-%m-%d"),
                "name": new_task,
                "user": user_name,
                "color": task_color
            }
            st.session_state.tasks.append(new_item)
            save_data(st.session_state.tasks) # 파일에 즉시 저장
            st.success(f"{user_name}님, 업무가 저장되었습니다!")
            st.rerun()

    # 4. 삭제 권한 관리 (관리자 lynnjh 만 가능)
    if user_name == "lynnhj" or user_name == "lynnjh": # 오타 대비 포함
        st.divider()
        st.subheader("🔒 관리자 메뉴 (삭제)")
        if st.session_state.tasks:
            task_to_delete = st.selectbox("삭제할 업무 선택", 
                                          options=st.session_state.tasks, 
                                          format_func=lambda x: f"[{x['date']}] {x['name']}")
            if st.button("선택한 업무 삭제", color_scheme="red"):
                st.session_state.tasks.remove(task_to_delete)
                save_data(st.session_state.tasks)
                st.warning("업무가 삭제되었습니다.")
                st.rerun()
        else:
            st.write("삭제할 업무가 없습니다.")

# --- 4. 메인 화면: 달력 내비게이션 및 출력 ---
st.title("📅 GS25 Team Work Calendar")

# 달력 컨트롤러
c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    if st.button("◀ 이전 달", use_container_width=True):
        if st.session_state.cal_month == 1:
            st.session_state.cal_month = 12
            st.session_state.cal_year -= 1
        else:
            st.session_state.cal_month -= 1
        st.rerun()
with c2:
    st.markdown(f"<h2 style='text-align: center;'>{st.session_state.cal_year}년 {st.session_state.cal_month}월</h2>", unsafe_allow_html=True)
with c3:
    if st.button("다음 달 ▶", use_container_width=True):
        if st.session_state.cal_month == 12:
            st.session_state.cal_month = 1
            st.session_state.cal_year += 1
        else:
            st.session_state.cal_month += 1
        st.rerun()

# 요일 헤더
days = ["일", "월", "화", "수", "목", "금", "토"]
head_cols = st.columns(7)
for i, d in enumerate(days):
    head_cols[i].markdown(f"<div style='text-align:center; font-weight:bold; color:#666; border-bottom:2px solid #0076BE; padding-bottom:5px;'>{d}</div>", unsafe_allow_html=True)

# 달력 날짜 생성
cal = calendar.Calendar(firstweekday=6)
month_days = cal.monthdayscalendar(st.session_state.cal_year, st.session_state.cal_month)

for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day == 0:
                st.write("")
            else:
                # 오늘 날짜 강조 디자인
                is_today = (datetime.now().year == st.session_state.cal_year and 
                            datetime.now().month == st.session_state.cal_month and 
                            datetime.now().day == day)
                today_style = "border: 2px solid #0076BE;" if is_today else ""
                
                st.markdown(f"""<div class="calendar-box" style="{today_style}">
                                <span style="font-size:18px; font-weight:bold;">{day}</span>""", unsafe_allow_html=True)
                
                # 해당 날짜 업무 필터링
                current_date = f"{st.session_state.cal_year}-{st.session_state.current_month:02d}-{day:02d}" # 기존 변수명 호환 유지
                current_date = f"{st.session_state.cal_year}-{st.session_state.cal_month:02d}-{day:02d}"
                
                day_tasks = [t for t in st.session_state.tasks if t['date'] == current_date]
                
                for task in day_tasks:
                    st.markdown(f"""
                        <div class="task-item" style="background-color: {task['color']}22; color: {task['color']}; border-left-color: {task['color']};">
                            <b>{task['name']}</b><br><span style="font-size:10px;">👤 {task['user']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
