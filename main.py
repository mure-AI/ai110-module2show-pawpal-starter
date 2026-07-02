"""Demo script for the PawPal scheduler.

Creates an owner with two pets, gives each pet some daily tasks at
different times, then prints today's organized schedule to the terminal.
"""

from datetime import date, time

from pawpal_system import Activity, Pet, Schedule, User


def main() -> None:
    # The owner and today's authoritative schedule.
    schedule = Schedule(day=date.today())
    owner = User(name="Murewa", schedule=schedule)

    # Two pets.
    rex = Pet(name="Rex", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(rex)
    owner.add_pet(luna)

    # Tasks added deliberately OUT OF time order, spread across both pets,
    # with one already complete to exercise the completed-last sorting.
    owner.add_activity(
        rex,
        Activity(
            name="Evening medication",
            start_time=time(18, 0),
            duration_minutes=10,
            priority=3,
            category="health",
            frequency="daily",
            is_fixed=True,
        ),
    )
    owner.add_activity(
        luna,
        Activity(
            name="Breakfast",
            start_time=time(8, 0),
            duration_minutes=15,
            priority=3,
            category="feeding",
            frequency="daily",
        ),
    )
    owner.add_activity(
        rex,
        Activity(
            name="Morning walk",
            start_time=time(7, 30),
            duration_minutes=30,
            priority=2,
            category="exercise",
            frequency="daily",
            is_complete=True,
        ),
    )
    owner.add_activity(
        luna,
        Activity(
            name="Litter cleanup",
            start_time=time(12, 0),
            duration_minutes=10,
            priority=1,
            category="hygiene",
            frequency="daily",
        ),
    )
    # Two tasks deliberately at the SAME time (08:00) to trigger a conflict.
    # Rex's "Breakfast" clashes with Luna's existing 08:00 "Breakfast", and
    # is fixed so resolve_conflicts won't quietly shift it away.
    owner.add_activity(
        rex,
        Activity(
            name="Breakfast",
            start_time=time(8, 0),
            duration_minutes=15,
            priority=3,
            category="feeding",
            frequency="daily",
            is_fixed=True,
        ),
    )

    # 1. Insertion order — proves the tasks really were added out of order.
    print("Tasks as added (insertion order):")
    for activity in schedule.activities:
        print(f"  {activity}")

    # 2. by_time() — sorted chronologically, completed tasks sink to the bottom.
    print("\nSorted by time (by_time):")
    for activity in schedule.by_time():
        print(f"  {activity}")

    # 3. filter(status=...) — completion status.
    print("\nPending only (filter status='pending'):")
    for activity in schedule.by_time(schedule.filter(status="pending")):
        print(f"  {activity}")

    print("\nComplete only (filter status='complete'):")
    for activity in schedule.filter(status="complete"):
        print(f"  {activity}")

    # 4. filter(pet_name=...) — new name-based filter, sorted by time.
    print("\nRex's tasks (filter pet_name='Rex'):")
    for activity in schedule.by_time(schedule.filter(pet_name="Rex")):
        print(f"  {activity}")

    # 5. Compose both — Luna's pending tasks, in time order.
    print("\nLuna's pending tasks (filter pet_name='Luna', status='pending'):")
    for activity in schedule.by_time(
        schedule.filter(pet_name="Luna", status="pending")
    ):
        print(f"  {activity}")

    # 6. Conflict detection — warn about tasks scheduled at the same time.
    #    Printed BEFORE build_daily_view, whose resolve_conflicts step may
    #    shift movable tasks apart.
    print("\nConflict check (conflict_warning):")
    if warning := schedule.conflict_warning():
        print(warning)
    else:
        print("  ✓ no conflicts")

    # The full organized agenda for context.
    print("\n" + schedule.build_daily_view())

    # 7. Focused verification: two tasks at the SAME time must be flagged.
    verify_two_tasks_conflict()


def verify_two_tasks_conflict() -> None:
    """Build a minimal schedule with two tasks at the same time and confirm
    the Scheduler identifies the clash and prints a warning."""
    print("\nVerify: two tasks at the same time")

    schedule = Schedule(day=date.today())
    owner = User(name="Tester", schedule=schedule)
    milo = Pet(name="Milo", species="dog")
    owner.add_pet(milo)

    # Two tasks deliberately scheduled at the exact same time (09:00).
    owner.add_activity(
        milo,
        Activity(name="Feed", start_time=time(9, 0), duration_minutes=15),
    )
    owner.add_activity(
        milo,
        Activity(name="Vet call", start_time=time(9, 0), duration_minutes=15),
    )

    conflicts = schedule.detect_conflicts()
    warning = schedule.conflict_warning()

    # The Scheduler should identify exactly one overlapping pair and warn.
    assert len(conflicts) == 1, f"expected 1 conflict, got {len(conflicts)}"
    assert warning, "expected a non-empty conflict warning"

    print(warning)
    print("  ✓ Scheduler correctly identified the conflict")


if __name__ == "__main__":
    main()
