import streamlit as st
import json
import os
from datetime import datetime
import calendar

# --- 1. 데이터 저장소 준비 (데이터 영구 보존) ---
DB_FILE = "tasks_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(tasks):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# --- 2. 기본 설정 및 GS25 디자인 테마 적용 ---
st.set_page_config(page_title="GS25 상생협력팀 업무달력", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #0076BE !important; font-family: 'Pretendard', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

if "tasks" not in st.session_state:
    st.session_state.tasks = load_data()
if "cal_year" not in st.session_state:
    st.session_state.cal_year = datetime.now().year
if "cal_month" not in st.session_state:
    st.session_state.cal_month = datetime.now().month

# --- 3. 사이드바: 아이디 확인 및 업무 등록 ---
with st.sidebar:
    st.title("GS25 상생협력팀")
    
    # 이 칸에 lynnjh를 적으면 관리자 모드가 켜집니다!
    user_name = st.text_input("👤 구글 아이디 (또는 이름)", placeholder="이름이나 ID 입력")
    
    st.divider()
    
    st.subheader("📝 신규 업무 등록")
    new_task = st.text_input("업무 내용을 적어주세요")
    task_color = st.color_picker("달력 표시 색상 선택", "#0076BE")
    task_date = st.date_input("날짜 선택", datetime.now())
    
    if st.button("업무 저장하기", use_container_width=True, type="primary"):
        if not user_name:
            st.error("아이디(이름)를 입력해주세요!")
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
            save_data(st.session_state.tasks)
            st.success("등록 성공!")
            st.rerun()

# --- 4. 메인 화면: 달력 내비게이션 ---
st.title("📅 GS25 Team Work Calendar")

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

# --- 5. 달력 날짜 생성 및 업무 렌더링 (핵심 기능!) ---
cal = calendar.Calendar(firstweekday=6)
month_days = cal.monthdayscalendar(st.session_state.cal_year, st.session_state.cal_month)

for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day != 0:
                is_today = (datetime.now().year == st.session_state.cal_year and 
                            datetime.now().month == st.session_state.cal_month and 
                            datetime.now().day == day)
                
                # 달력 네모 칸을 스트림릿 고유 기능(container)으로 만들어서 삐져나오지 않게 고정!
                with st.container(border=True, height=160):
                    if is_today:
                        st.markdown(f"<span style='color:#0076BE; font-size:16px; font-weight:bold;'>{day} (오늘)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='font-size:16px; font-weight:bold;'>{day}</span>", unsafe_allow_html=True)
                    
                    # 해당 날짜의 업무 필터링
                    current_date = f"{st.session_state.cal_year}-{st.session_state.cal_month:02d}-{day:02d}"
                    day_tasks = [t for t in st.session_state.tasks if t['date'] == current_date]
                    
                    for task in day_tasks:
                        # 🌟 관리자(lynnjh)인 경우: 달력 안에서 클릭하면 수정/삭제 팝업창이 뜸!
                        if user_name in ["lynnjh", "lynnhj"]:
                            with st.popover(f"🔧 {task['name']}", use_container_width=True):
                                # 수정할 수 있는 입력칸 제공
                                edit_name = st.text_input("업무명 수정", task['name'], key=f"n_{task['id']}")
                                edit_color = st.color_picker("색상 수정", task['color'], key=f"c_{task['id']}")
                                
                                # 버튼 두 개 나란히 배치 (수정 / 삭제)
                                bc1, bc2 = st.columns(2)
                                if bc1.button("저장", key=f"u_{task['id']}", type="primary"):
                                    for t in st.session_state.tasks:
                                        if t['id'] == task['id']:
                                            t['name'] = edit_name
                                            t['color'] = edit_color
                                    save_data(st.session_state.tasks)
                                    st.rerun()
                                    
                                if bc2.button("삭제", key=f"d_{task['id']}"):
                                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                                    save_data(st.session_state.tasks)
                                    st.rerun()
                                    
                        # 🌟 일반 사용자인 경우: 그냥 예쁜 네모 박스로 보기만 가능!
                        else:
                            st.markdown(f"""
                                <div style="background-color: {task['color']}15; color: #333; border-left: 5px solid {task['color']}; padding: 4px 6px; border-radius: 4px; margin-bottom: 4px; font-size: 11px; font-weight: bold; line-height: 1.3;">
                                    {task['name']}<br><span style="font-size:9px; color:#777;">👤 {task['user']}</span>
                                </div>
                            """, unsafe_allow_html=True)
