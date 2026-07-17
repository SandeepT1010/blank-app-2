import streamlit as st
from datetime import date

st.title("Smart Study Planner")

subject = st.text_input("Subject")
task_name = st.text_input("Task name")
deadline = st.date_input("Deadline", min_value=date.today())
study_hours = st.number_input(
    "Study hours needed",
    min_value=1,
    max_value=20,
    value=1
)
priority = st.selectbox(
    "Priority",
    ["Low", "Medium", "High"]
)

if st.button("Add Task"):
    if subject and task_name:
        st.success("Task added!")

        st.write("### Task Information")
        st.write("**Subject:**", subject)
        st.write("**Task:**", task_name)
        st.write("**Deadline:**", deadline)
        st.write("**Hours needed:**", study_hours)
        st.write("**Priority:**", priority)
    else:
        st.warning("Enter the subject and task name.")