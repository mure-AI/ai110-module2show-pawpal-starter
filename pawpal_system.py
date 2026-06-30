"""PawPal system classes implemented from diagrams/uml_draft.mmd.

Class mapping (UML name -> conceptual role from the spec):
    Activity -> Task     : a single pet-care activity
    Pet      -> Pet      : pet details + its activities
    Schedule -> Scheduler: the "brain" that organizes activities across pets
    User     -> Owner    : owns multiple pets and exposes all their activities
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta


@dataclass
class Activity:
    """A single pet-care activity (the "Task").

    Holds a description (``name``), a target time, how often it recurs
    (``frequency``), and whether it has been completed.
    """

    name: str
    pet: "Pet | None" = None
    priority: int = 1
    start_time: time | None = None
    duration_minutes: int = 15
    category: str = "general"
    frequency: str = "daily"  # e.g. "once", "daily", "weekly"
    earliest: time | None = None
    latest: time | None = None
    is_fixed: bool = False
    is_complete: bool = False

    def mark_complete(self) -> None:
        """Mark this activity as done."""
        self.is_complete = True

    @property
    def end_time(self) -> time | None:
        """When this activity finishes, based on ``start_time`` + duration."""
        if self.start_time is None:
            return None
        start = datetime.combine(date.min, self.start_time)
        return (start + timedelta(minutes=self.duration_minutes)).time()

    def overlaps(self, other: "Activity") -> bool:
        """Return True if this activity's time window overlaps ``other``'s."""
        if self.start_time is None or other.start_time is None:
            return False
        return self.start_time < other.end_time and other.start_time < self.end_time

    def __str__(self) -> str:
        when = self.start_time.strftime("%H:%M") if self.start_time else "unscheduled"
        status = "✓" if self.is_complete else "○"
        pet_name = self.pet.name if self.pet else "—"
        return f"{status} {when} {self.name} ({pet_name}, {self.duration_minutes}m, p{self.priority})"


@dataclass
class Pet:
    """A pet: stores its details and the list of activities that belong to it."""

    name: str
    species: str = "other"
    activities: list[Activity] = field(default_factory=list)

    def add_activity(self, activity: Activity) -> None:
        """Attach an activity to this pet."""
        activity.pet = self
        self.activities.append(activity)

    def pending_activities(self) -> list[Activity]:
        """Activities for this pet that are not yet complete."""
        return [a for a in self.activities if not a.is_complete]

    def display_schedule(self) -> None:
        """Print this pet's activities, ordered by time."""
        print(f"Schedule for {self.name} ({self.species}):")
        ordered = sorted(
            self.activities,
            key=lambda a: a.start_time or time.max,
        )
        if not ordered:
            print("  (no activities)")
            return
        for activity in ordered:
            print(f"  {activity}")


@dataclass
class Schedule:
    """The "brain": retrieves, organizes, and manages activities across pets."""

    day: date
    activities: list[Activity] = field(default_factory=list)

    def add_activity(self, activity: Activity) -> None:
        """Register an activity in the day's authoritative schedule."""
        if activity not in self.activities:
            self.activities.append(activity)

    def prioritize(self) -> list[Activity]:
        """Return activities ordered for the day.

        Fixed-time activities and higher priorities come first; among equal
        priorities, earlier start times win. Completed activities sink to the
        bottom so the daily view leads with what's left to do.
        """
        return sorted(
            self.activities,
            key=lambda a: (
                a.is_complete,
                not a.is_fixed,
                -a.priority,
                a.start_time or time.max,
            ),
        )

    def resolve_conflicts(self) -> None:
        """Push back movable activities that overlap an earlier one.

        Fixed activities never move. A movable activity that overlaps the
        previous one is shifted to start when the previous activity ends, as
        long as that stays within its ``latest`` bound.
        """
        ordered = sorted(
            (a for a in self.activities if a.start_time is not None),
            key=lambda a: a.start_time,
        )
        previous: Activity | None = None
        for activity in ordered:
            if previous is not None and activity.overlaps(previous):
                if not activity.is_fixed and previous.end_time is not None:
                    if activity.latest is None or previous.end_time <= activity.latest:
                        activity.start_time = previous.end_time
            previous = activity

    def build_daily_view(self) -> str:
        """Return a time-ordered agenda for the day, in aligned columns.

        Reads top-to-bottom like a real agenda: earliest first, with a
        start–end time range, aligned name/pet/category columns, and tags
        for priority and fixed-time activities.
        """
        self.resolve_conflicts()
        ordered = sorted(
            self.activities,
            key=lambda a: (a.start_time or time.max, a.is_complete),
        )

        weekday = self.day.strftime("%A, %B %-d, %Y")
        header = f"PawPal+ plan — {weekday}"
        rule = "─" * len(header)
        lines = [header, rule]

        if not ordered:
            lines.append("  (nothing scheduled)")
            lines.append(rule)
            return "\n".join(lines)

        # Column widths sized to the actual content so everything lines up.
        name_w = max(len(a.name) for a in ordered)
        pet_w = max(len((a.pet.name if a.pet else "—")) for a in ordered)
        cat_w = max(len(a.category) for a in ordered)

        for activity in ordered:
            lines.append(self._format_row(activity, name_w, pet_w, cat_w))

        done = sum(1 for a in ordered if a.is_complete)
        todo = len(ordered) - done
        pets = len({id(a.pet) for a in ordered if a.pet})
        lines.append(rule)
        lines.append(
            f"  {len(ordered)} tasks across {pets} pets · "
            f"{done} done, {todo} to go"
        )
        return "\n".join(lines)

    def build_priority_view(self) -> str:
        """Return a plan ordered by priority (not time), with reasoning.

        This is the original priority-led ordering: fixed-time and
        higher-priority activities lead, completed ones sink to the bottom.
        """
        self.resolve_conflicts()
        ordered = self.prioritize()
        lines = [f"PawPal+ plan for {self.day.isoformat()}:"]
        if not ordered:
            lines.append("  (nothing scheduled)")
            return "\n".join(lines)
        for activity in ordered:
            reason = self._explain(activity)
            lines.append(f"  {activity} — {reason}")
        return "\n".join(lines)

    @staticmethod
    def _format_row(activity: Activity, name_w: int, pet_w: int, cat_w: int) -> str:
        """Format one activity as an aligned agenda row for ``build_daily_view``."""
        if activity.start_time is None:
            when = "  unscheduled  "
        else:
            start = activity.start_time.strftime("%H:%M")
            end = activity.end_time.strftime("%H:%M") if activity.end_time else "  ?  "
            when = f"{start} – {end}"

        pet_name = activity.pet.name if activity.pet else "—"

        tags = []
        if activity.is_complete:
            tags.append("✓ done")
        if activity.priority >= 3:
            tags.append("★ high")
        if activity.is_fixed:
            tags.append("📌 fixed")
        tag_str = ("  " + "  ".join(tags)) if tags else ""

        return (
            f"  {when}   "
            f"{activity.name:<{name_w}}   "
            f"{pet_name:<{pet_w}}   "
            f"{activity.category:<{cat_w}}"
            f"{tag_str}"
        )

    @staticmethod
    def _explain(activity: Activity) -> str:
        """Explain why an activity is placed where it is."""
        if activity.is_complete:
            return "already done"
        reasons = []
        if activity.is_fixed:
            reasons.append("fixed time")
        if activity.priority >= 3:
            reasons.append("high priority")
        elif activity.priority <= 1:
            reasons.append("low priority")
        reasons.append(f"{activity.frequency}")
        return ", ".join(reasons)


@dataclass
class User:
    """The owner: manages multiple pets and provides access to all activities."""

    name: str
    schedule: Schedule
    pets: list[Pet] = field(default_factory=list)
    constraints: list[dict] = field(default_factory=list)
    preferences: list[dict] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet, syncing any activities it already has into the schedule."""
        if pet not in self.pets:
            self.pets.append(pet)
        for activity in pet.activities:
            self.schedule.add_activity(activity)

    def add_constraint(self, constraint: dict) -> None:
        """Record a scheduling constraint for this owner."""
        self.constraints.append(constraint)

    def add_preference(self, preference: dict) -> None:
        """Record a scheduling preference for this owner."""
        self.preferences.append(preference)

    def add_activity(self, pet: Pet, activity: Activity) -> None:
        """Add an activity to a pet and the authoritative schedule together."""
        pet.add_activity(activity)
        self.schedule.add_activity(activity)

    def all_activities(self) -> list[Activity]:
        """Every activity across all of this owner's pets."""
        return [activity for pet in self.pets for activity in pet.activities]
