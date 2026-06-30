"""PawPal system class skeletons generated from diagrams/uml_draft.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class Activity:
    name: str
    pet: "Pet"
    priority: int
    start_time: time
    duration_minutes: int
    category: str
    earliest: time
    latest: time
    is_fixed: bool


@dataclass
class Pet:
    name: str
    activities: list[Activity] = field(default_factory=list)

    def display_schedule(self) -> None:
        ...

    def add_activity(self, activity: Activity) -> None:
        ...


@dataclass
class Schedule:
    day: date
    activities: list[Activity] = field(default_factory=list)

    def add_activity(self, activity: Activity) -> None:
        ...

    def prioritize(self) -> list[Activity]:
        ...

    def build_daily_view(self) -> str:
        ...

    def resolve_conflicts(self) -> None:
        ...


@dataclass
class User:
    name: str
    schedule: Schedule
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        ...

    def add_constraint(self, constraint) -> None:
        ...

    def add_preference(self, preference) -> None:
        ...

    def add_activity(self, pet: Pet, activity: Activity) -> None:
        ...
