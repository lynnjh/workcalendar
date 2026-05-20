import streamlit as st
import json
import os
from datetime import datetime
import calendar
import pandas as pd  # 리스트(나열식) 뷰를 그리기 위해 추가

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

# --- 🌟 [핵심] 실제 Streamlit 계정 로그인 여부 확인 ---
is_admin = False
try:
    # 스트림릿 서버에 현재 접속한 유저의 이메일 정보를 가져옵니다.
    user_email = ""
    if hasattr(st, "user") and hasattr(st.user, "email"):
        user_email = st.user.email
    elif hasattr(st, "experimental_user") and hasattr(st.experimental_user, "email"):
        user_email = st.experimental_user.email
        
    # 가져온 이메일 주소에 'lynnjh'가 포함되어 있다면 관리자(True)로 인정!
    if user_email and "lynnjh" in user_email.lower():
        is_admin = True
except:
    pass

# --- 3. 사이드바: 업무 등록 ---
with st.sidebar:
    st.title("GS25 상생협력팀")
    
    # 수정 1: 라벨명 변경
    user_name = st.text_input("👤 이름 (예: 이준호 매니저)", placeholder="본인 이름을 적어주세요")
    
    st.divider()
    
    st.subheader("📝 신규 업무 등록")
    new_task = st.text_input("업무 내용을 적어주세요")
    task_color = st.color_picker("달력 표시 색상 선택", "#0076BE")
    task_date = st.date_input("날짜 선택", datetime.now())
    
    if st.button("업무 저장하기", use_container_width=True, type="primary"):
        if not user_name:
            st.error("이름을 입력해주세요!")
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

# --- 4. 메인 화면 ---
st.title("GS25 Team Work Calendar")

# 관리자(lynnjh)로 로그인된 상태라면 환영 메시지 및 안내 표시
if is_admin:
    st.info("🔐 **관리자(lynnjh) 계정으로 인증되었습니다.** 달력 내에서 업무를 즉시 수정/삭제할 수 있습니다.")

# 수정 3: 달력 뷰와 리스트 뷰를 탭(Tab)으로 나누기
tab_cal, tab_list = st.tabs(["📅 달력(월별) 뷰", "📝 전체 리스트(나열식) 뷰"])

# ==========================================
# 탭 1: 기존 달력 화면
# ==========================================
with tab_cal:
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
                    
                    with st.container(border=True, height=160):
                        if is_today:
                            st.markdown(f"<span style='color:#0076BE; font-size:16px; font-weight:bold;'>{day} (오늘)</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='font-size:16px; font-weight:bold;'>{day}</span>", unsafe_allow_html=True)
                        
                        current_date = f"{st.session_state.cal_year}-{st.session_state.cal_month:02d}-{day:02d}"
                        day_tasks = [t for t in st.session_state.tasks if t['date'] == current_date]
                        
                        for task in day_tasks:
                            # 🌟 수정 2: 사이드바 이름이 아니라 '실제 로그인 계정(is_admin)' 기준으로 권한 부여
                            if is_admin:
                                with st.popover(f"🔧 {task['name']}", use_container_width=True):
                                    edit_name = st.text_input("업무명 수정", task['name'], key=f"n_{task['id']}")
                                    edit_color = st.color_picker("색상 수정", task['color'], key=f"c_{task['id']}")
                                    
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
                            else:
                                st.markdown(f"""
                                    <div style="background-color: {task['color']}15; color: #333; border-left: 5px solid {task['color']}; padding: 4px 6px; border-radius: 4px; margin-bottom: 4px; font-size: 11px; font-weight: bold; line-height: 1.3;">
                                        {task['name']}<br><span style="font-size:9px; color:#777;">👤 {task['user']}</span>
                                    </div>
                                """, unsafe_allow_html=True)

# ==========================================
# 탭 2: 나열식 리스트 화면
# ==========================================
with tab_list:
    st.subheader("업무 전체 리스트")
    if not st.session_state.tasks:
        st.write("등록된 업무가 없습니다.")
    else:
        # 데이터를 표(Dataframe) 형식으로 변환하여 예쁘게 나열
        df = pd.DataFrame(st.session_state.tasks)
        # 필요한 항목만 뽑아서 순서대로 정렬
        df = df[["date", "name", "user"]]
        df.columns = ["날짜", "업무명", "담당자"]
        df = df.sort_values(by="날짜", ascending=True).reset_index(drop=True)
        
        # 스트림릿의 인터랙티브 표 기능 사용 (클릭해서 정렬 가능)
        st.dataframe(df, use_container_width=True, hide_index=True)
