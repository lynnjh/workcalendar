import streamlit as st
from datetime import datetime
import calendar

st.set_page_config(layout="wide")

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "current_year" not in st.session_state:
    st.session_state.current_year = datetime.now().year
if "current_month" not in st.session_state:
    st.session_state.current_month = datetime.now().month

# --- 사이드바: 업무 등록 ---
with st.sidebar:
    st.header("🗓️ 팀 업무 등록")
    st.write("달력에 표시할 업무를 입력하세요.")
    
    task_name = st.text_input("업무명", placeholder="예: 상생 정보통 5월호 기획안 작성")
    owner = st.selectbox("담당자", ["이준호 매니저", "김팀장", "박대리", "최사원"])
    priority = st.radio("중요도", ["상", "중", "하"], index=1, horizontal=True)
    task_date = st.date_input("날짜", datetime.now())
    
    if st.button("업무 저장하기", use_container_width=True):
        if task_name:
            st.session_state.tasks.append({
                "date": task_date.strftime("%Y-%m-%d"),
                "name": task_name,
                "owner": owner,
                "priority": priority
            })
            st.success("등록 완료!")
        else:
            st.error("업무명을 적어주세요.")

# --- 메인 화면: 달력 ---
st.title("📅 팀 업무 관리 달력")

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("◀ 이전 달", use_container_width=True):
        st.session_state.current_month -= 1
        if st.session_state.current_month < 1:
            st.session_state.current_month = 12
            st.session_state.current_year -= 1
with col2:
    st.markdown(f"<h3 style='text-align: center;'>{st.session_state.current_year}년 {st.session_state.current_month}월</h3>", unsafe_allow_html=True)
with col3:
    if st.button("다음 달 ▶", use_container_width=True):
        st.session_state.current_month += 1
        if st.session_state.current_month > 12:
            st.session_state.current_month = 1
            st.session_state.current_year += 1

cal = calendar.Calendar(firstweekday=6)
weeks = cal.monthdayscalendar(st.session_state.current_year, st.session_state.current_month)

days_of_week = ["일", "월", "화", "수", "목", "금", "토"]
cols = st.columns(7)
for i, day in enumerate(days_of_week):
    cols[i].markdown(f"<p style='text-align: center; font-weight: bold; background-color: #f0f2f6; padding: 5px; border-radius: 5px;'>{day}</p>", unsafe_allow_html=True)

importance_colors = {"상": "#ffebee", "중": "#fff8e1", "하": "#e8f5e9"}

for week in weeks:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day != 0:
                st.markdown(f"**{day}**")
                target_date = f"{st.session_state.current_year}-{st.session_state.current_month:02d}-{day:02d}"
                day_tasks = [t for t in st.session_state.tasks if t["date"] == target_date]
                
                for task in day_tasks:
                    bg_color = importance_colors.get(task["priority"], "#ffffff")
                    st.markdown(
                        f"<div style='background-color: {bg_color}; padding: 6px; border-radius: 4px; margin-bottom: 4px; font-size: 12px; border-left: 4px solid gray;'>"
                        f"<b>{task['name']}</b><br><span style='color: #555;'>👤 {task['owner']}</span>"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
            st.markdown("<hr style='margin: 10px 0; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)
