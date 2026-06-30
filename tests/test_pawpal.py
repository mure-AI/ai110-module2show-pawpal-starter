"""Tests for the PawPal system.

In the UML, a "task" is an ``Activity`` and a pet's "task count" is the
number of activities attached to that pet.
"""

from pawpal_system import Activity, Pet


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
