"""Tests for the PawPal system.

In the UML, a "task" is an ``Activity`` and a pet's "task count" is the
number of activities attached to that pet.
"""

from datetime import date, time

from pawpal_system import Activity, Pet, Schedule


def test_mark_complete_changes_status():
    """mark_complete() should flip an activity from incomplete to complete."""
    task = Activity(name="Walk")
    assert task.is_complete is False

    task.mark_complete()

    assert task.is_complete is True


def test_add_activity_increases_pet_task_count():
    """Adding a task to a pet should increase that pet's task count by one."""
    pet = Pet(name="Rex", species="dog")
    assert len(pet.activities) == 0

    pet.add_activity(Activity(name="Feed"))

    assert len(pet.activities) == 1


def test_by_time_returns_chronological_order():
    """Sorting correctness: by_time() returns tasks in ascending time order."""
    schedule = Schedule(day=date(2026, 7, 1))
    noon = Activity(name="Lunch walk", start_time=time(12, 0))
    morning = Activity(name="Breakfast", start_time=time(8, 0))
    evening = Activity(name="Dinner", start_time=time(18, 30))
    for task in (noon, morning, evening):
        schedule.add_activity(task)

    ordered = schedule.by_time()

    assert [a.name for a in ordered] == ["Breakfast", "Lunch walk", "Dinner"]


def test_by_time_places_unscheduled_last():
    """Sorting edge case: tasks with no start_time sort to the bottom."""
    schedule = Schedule(day=date(2026, 7, 1))
    scheduled = Activity(name="Walk", start_time=time(9, 0))
    unscheduled = Activity(name="Vet call", start_time=None)
    schedule.add_activity(unscheduled)
    schedule.add_activity(scheduled)

    ordered = schedule.by_time()

    assert [a.name for a in ordered] == ["Walk", "Vet call"]


def test_completing_daily_task_spawns_next_day():
    """Recurrence logic: completing a daily task creates one for the next day."""
    schedule = Schedule(day=date(2026, 7, 1))
    pet = Pet(name="Rex", species="dog")
    walk = Activity(
        name="Morning walk",
        pet=pet,
        frequency="daily",
        start_date=date(2026, 7, 1),
        start_time=time(8, 0),
    )
    pet.add_activity(walk)
    schedule.add_activity(walk)

    nxt = schedule.complete(walk)

    assert walk.is_complete is True
    assert nxt is not None
    assert nxt.is_complete is False
    assert nxt.start_date == date(2026, 7, 2)
    # The new instance is attached to both the same pet and the schedule, once each.
    assert pet.activities.count(nxt) == 1
    assert schedule.activities.count(nxt) == 1


def test_completing_once_task_spawns_nothing():
    """Recurrence edge case: a non-recurring 'once' task has no next occurrence."""
    schedule = Schedule(day=date(2026, 7, 1))
    task = Activity(name="Grooming", frequency="once", start_date=date(2026, 7, 1))
    schedule.add_activity(task)

    assert schedule.complete(task) is None
    assert len(schedule.activities) == 1


def test_detect_conflicts_flags_overlapping_times():
    """Conflict detection: overlapping (duplicate) time windows are flagged."""
    schedule = Schedule(day=date(2026, 7, 1))
    a = Activity(name="Feed cat", start_time=time(8, 0), duration_minutes=30)
    b = Activity(name="Walk dog", start_time=time(8, 15), duration_minutes=30)
    schedule.add_activity(a)
    schedule.add_activity(b)

    conflicts = schedule.detect_conflicts()

    assert len(conflicts) == 1
    assert conflicts[0] == (a, b)


def test_detect_conflicts_ignores_back_to_back():
    """Conflict edge case: touching windows (end == next start) do not conflict."""
    schedule = Schedule(day=date(2026, 7, 1))
    a = Activity(name="Feed", start_time=time(8, 0), duration_minutes=15)
    b = Activity(name="Walk", start_time=time(8, 15), duration_minutes=15)
    schedule.add_activity(a)
    schedule.add_activity(b)

    assert schedule.detect_conflicts() == []
