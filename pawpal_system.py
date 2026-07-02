"""PawPal system classes implemented from diagrams/uml_draft.mmd.

Class mapping (UML name -> conceptual role from the spec):
    Activity -> Task     : a single pet-care activity
    Pet      -> Pet      : pet details + its activities
    Schedule -> Scheduler: the "brain" that organizes activities across pets
    User     -> Owner    : owns multiple pets and exposes all their activities
"""

from __future__ import annotations

import copy
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
    start_date: date | None = None  # anchor date for "once"/"weekly" recurrence
    earliest: time | None = None
    latest: time | None = None
    is_fixed: bool = False
    is_complete: bool = False

    def mark_complete(self) -> None:
        """Mark this activity as done."""
        self.is_complete = True

    def next_occurrence(self) -> "Activity | None":
        """Build the next recurring instance of this activity, or ``None``.

        Only ``daily`` (+1 day) and ``weekly`` (+7 days) recur; ``once`` and
        any other frequency return ``None``. The clone keeps every field but
        starts pending, with ``start_date`` advanced from this one's date (or
        today if it has none). Pure: this activity is not mutated, and the
        clone is detached from any pet/schedule so the caller decides where it
        lives.
        """
        interval = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}.get(
            self.frequency
        )
        if interval is None:
            return None

        nxt = copy.copy(self)
        nxt.is_complete = False
        nxt.start_date = (self.start_date or date.today()) + interval
        return nxt

    def occurs_on(self, day: date) -> bool:
        """Return True if this activity should appear on ``day``.

        ``daily`` always occurs. ``weekly`` recurs on the weekday of its
        ``start_date``. ``once`` occurs only on its ``start_date``. With no
        ``start_date`` set, the activity always occurs (so simple demos that
        omit a date still show every task).
        """
        if self.frequency == "daily":
            return True
        if self.start_date is None:
            return True
        if self.frequency == "weekly":
            return day.weekday() == self.start_date.weekday()
        if self.frequency == "once":
            return day == self.start_date
        return True

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
        """Return a one-line summary: status glyph, time, name, and details.

        Shows ``✓``/``○`` for done/pending, the start time as ``HH:MM`` (or
        ``unscheduled`` when unset), the owning pet's name (or ``—`` when
        detached), the duration, and the priority as ``p{n}``.
        """
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

    def complete(self, activity: Activity) -> Activity | None:
        """Mark ``activity`` done and auto-schedule its next occurrence.

        For ``daily``/``weekly`` activities this spawns the next instance via
        ``Activity.next_occurrence`` and attaches it to the same pet (if any)
        and to this schedule, mirroring ``User.add_activity``. Returns the new
        instance, or ``None`` for non-recurring activities.
        """
        activity.mark_complete()
        nxt = activity.next_occurrence()
        if nxt is None:
            return None
        if nxt.pet is not None:
            nxt.pet.activities.append(nxt)
        self.add_activity(nxt)
        return nxt

    def by_time(self, activities: list[Activity] | None = None) -> list[Activity]:
        """Return activities sorted by start time, completed ones last.

        Unscheduled activities (no ``start_time``) sort to the bottom. Among
        activities at the same time, pending sorts before complete. Pure: the
        input is not mutated.
        """
        source = self.activities if activities is None else activities
        return sorted(
            source,
            key=lambda a: (a.start_time or time.max, a.is_complete),
        )

    def filter(
        self,
        pet: "Pet | None" = None,
        pet_name: str | None = None,
        status: str | None = None,
    ) -> list[Activity]:
        """Return activities matching ``pet``, ``pet_name``, and/or ``status``.

        ``pet`` matches by identity. ``pet_name`` matches every activity whose
        pet shares that name — so duplicate pet names all match. ``status``
        accepts ``"pending"``, ``"complete"``, or ``None`` for all. Pure and
        composable: ``self.by_time(self.filter(pet_name="Rex", status="pending"))``.
        """
        result = self.activities
        if pet is not None:
            result = [a for a in result if a.pet is pet]
        if pet_name is not None:
            result = [a for a in result if a.pet is not None and a.pet.name == pet_name]
        if status == "pending":
            result = [a for a in result if not a.is_complete]
        elif status == "complete":
            result = [a for a in result if a.is_complete]
        return list(result)

    def active_for_day(self) -> list[Activity]:
        """Activities whose recurrence places them on this schedule's day."""
        return [a for a in self.activities if a.occurs_on(self.day)]

    def detect_conflicts(self) -> list[tuple[Activity, Activity]]:
        """Return pairs of scheduled activities whose times overlap.

        Read-only: a time-ordered sweep that tracks the running latest end so
        each activity is compared against every earlier overlapping one, not
        just its immediate predecessor. Unlike ``resolve_conflicts`` it never
        mutates — callers can surface conflicts without shifting any times.
        """
        ordered = self.by_time([a for a in self.activities if a.start_time is not None])
        conflicts: list[tuple[Activity, Activity]] = []
        active: list[Activity] = []
        for activity in ordered:
            active = [a for a in active if a.end_time and a.end_time > activity.start_time]
            for earlier in active:
                conflicts.append((earlier, activity))
            active.append(activity)
        return conflicts

    def conflicts_by_pet(
        self,
    ) -> tuple[list[tuple[Activity, Activity]], list[tuple[Activity, Activity]]]:
        """Split overlapping pairs into same-pet and cross-pet conflicts.

        Returns ``(same_pet, cross_pet)``. A same-pet conflict is impossible
        for one pet to honor (it can't be two places at once); a cross-pet
        conflict only matters to the owner's own time. Pairs with an
        unassigned pet on either side count as cross-pet. Builds on
        ``detect_conflicts`` so the overlap logic lives in one place.
        """
        same_pet: list[tuple[Activity, Activity]] = []
        cross_pet: list[tuple[Activity, Activity]] = []
        for earlier, later in self.detect_conflicts():
            if earlier.pet is not None and earlier.pet is later.pet:
                same_pet.append((earlier, later))
            else:
                cross_pet.append((earlier, later))
        return same_pet, cross_pet

    def conflict_warning(self) -> str:
        """Return a human-readable warning about time conflicts, or ``""``.

        A lightweight, never-raising summary meant for printing: empty string
        when nothing overlaps, otherwise one ``⚠`` line per clashing pair with
        same-pet conflicts (the ones a single pet can't honor) listed first.
        Callers can guard with ``if msg := schedule.conflict_warning():``.
        """
        same_pet, cross_pet = self.conflicts_by_pet()
        if not same_pet and not cross_pet:
            return ""

        def when(activity: Activity) -> str:
            return activity.start_time.strftime("%H:%M") if activity.start_time else "??:??"

        def line(earlier: Activity, later: Activity, kind: str) -> str:
            return (
                f"  ⚠ {kind}: {earlier.name} ({when(earlier)}) overlaps "
                f"{later.name} ({when(later)})"
            )

        total = len(same_pet) + len(cross_pet)
        lines = [f"{total} scheduling conflict{'s' if total != 1 else ''} found:"]
        for earlier, later in same_pet:
            lines.append(line(earlier, later, f"same pet ({earlier.pet.name})"))
        for earlier, later in cross_pet:
            lines.append(line(earlier, later, "different pets"))
        return "\n".join(lines)

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
        ordered = self.by_time(self.active_for_day())

        # Any activity still overlapping another after resolution is flagged.
        conflicting = {id(a) for pair in self.detect_conflicts() for a in pair}

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
            lines.append(
                self._format_row(
                    activity, name_w, pet_w, cat_w, id(activity) in conflicting
                )
            )

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
        active = self.active_for_day()
        ordered = [a for a in self.prioritize() if a in active]
        lines = [f"PawPal+ plan for {self.day.isoformat()}:"]
        if not ordered:
            lines.append("  (nothing scheduled)")
            return "\n".join(lines)
        for activity in ordered:
            reason = self._explain(activity)
            lines.append(f"  {activity} — {reason}")
        return "\n".join(lines)

    @staticmethod
    def _format_row(
        activity: Activity,
        name_w: int,
        pet_w: int,
        cat_w: int,
        has_conflict: bool = False,
    ) -> str:
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
        if has_conflict:
            tags.append("⚠ conflict")
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
