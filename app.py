from datetime import date, datetime, time

import streamlit as st

from pawpal_system import User as Owner, Pet, Activity as Task, Schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    start_time = st.time_input("Start time", value=time(8, 0))

# Map the UI's text priority onto the backend's numeric scale.
PRIORITY_LEVELS = {"low": 1, "medium": 2, "high": 3}

if st.button("Add task"):
    st.session_state.tasks.append(
        {
            "title": task_title,
            "duration_minutes": int(duration),
            "priority": priority,
            "start_time": start_time.strftime("%H:%M"),
        }
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

view_mode = st.radio(
    "View", ["By time (daily agenda)", "By priority (with reasoning)"], horizontal=True
)

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.info("No tasks yet. Add at least one task above.")
    else:
        # Build the domain objects from the demo inputs using the backend methods.
        schedule = Schedule(day=date.today())
        owner = Owner(name=owner_name, schedule=schedule)
        pet = Pet(name=pet_name, species=species)
        owner.add_pet(pet)

        for t in st.session_state.tasks:
            task = Task(
                name=t["title"],
                priority=PRIORITY_LEVELS.get(t["priority"], 1),
                start_time=datetime.strptime(t["start_time"], "%H:%M").time(),
                duration_minutes=t["duration_minutes"],
            )
            owner.add_activity(pet, task)

        if view_mode.startswith("By time"):
            plan = schedule.build_daily_view()
        else:
            plan = schedule.build_priority_view()

        st.code(plan)
