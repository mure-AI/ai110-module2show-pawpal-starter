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

    # At least three tasks, at different times, spread across both pets.
    owner.add_activity(
        rex,
        Activity(
            name="Morning walk",
            start_time=time(7, 30),
            duration_minutes=30,
            priority=2,
            category="exercise",
            frequency="daily",
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
            name="Evening medication",
            start_time=time(18, 0),
            duration_minutes=10,
            priority=3,
            category="health",
            frequency="daily",
            is_fixed=True,
        ),
    )

    # Print today's organized schedule across all pets.
    print(schedule.build_daily_view())
 


if __name__ == "__main__":
    main()
