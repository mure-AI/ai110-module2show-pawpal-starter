# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
PawPal+ plan — Tuesday, June 30, 2026
─────────────────────────────────────
  07:30 – 08:00   Morning walk         Rex    exercise
  08:00 – 08:15   Breakfast            Luna   feeding   ★ high
  18:00 – 18:10   Evening medication   Rex    health    ★ high  📌 fixed
─────────────────────────────────────
  3 tasks across 2 pets · 0 done, 3 to go
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The tests in [tests/test_pawpal.py](tests/test_pawpal.py) cover the core scheduling behaviors:

- **Basics** — `mark_complete()` flips a task's status; adding a task grows the pet's task list.
- **Sorting correctness** — `Schedule.by_time()` returns tasks in chronological order and pushes unscheduled tasks (no `start_time`) to the bottom.
- **Recurrence logic** — completing a `daily` task spawns one pending instance for the next day (attached once to both pet and schedule), while a `once` task spawns nothing.
- **Conflict detection** — overlapping time windows are flagged as a pair, and back-to-back tasks (end == next start) are correctly *not* flagged.

Successful test run:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/asunke/Documents/Code files/CodePath/A110/Module_2/ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 8 items

tests/test_pawpal.py ........                                            [100%]

============================== 8 passed in 0.01s ===============================
```

### Confidence Level: ★★★★☆ (4 / 5)

All 8 tests pass and they exercise the trickiest logic — chronological sorting, daily recurrence spawning, and overlap detection including the strict-boundary edge case. Docking one star because coverage is not yet exhaustive: `weekly` recurrence, `resolve_conflicts()` (fixed tasks + `latest` bounds), cascading/transitive conflicts, and the priority-ordered view (`prioritize()`) are documented but not yet directly tested.

## 📐 Smarter Scheduling

The scheduling "brain" lives in the `Schedule` class in [pawpal_system.py](pawpal_system.py), with per-task logic on `Activity`. Each feature below names the method that implements it.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Schedule.by_time()`, `Schedule.prioritize()` | Time-ordered vs. priority-ordered views |
| Filtering | `Schedule.filter()`, `Schedule.active_for_day()`, `Pet.pending_activities()` | By pet, completion status, or day |
| Conflict handling | `Schedule.detect_conflicts()`, `Schedule.conflicts_by_pet()`, `Schedule.conflict_warning()`, `Schedule.resolve_conflicts()`, `Activity.overlaps()` | Detect, classify, warn, and auto-resolve overlaps |
| Recurring tasks | `Activity.next_occurrence()`, `Activity.occurs_on()`, `Schedule.complete()` | Daily/weekly/once recurrence |

### Sorting behavior

Two orderings are offered so the same set of tasks can be viewed either as an agenda or as a priority list:

- **`Schedule.by_time()`** — sorts by `start_time`, pushing unscheduled tasks (no `start_time`) to the bottom and, among tasks at the same time, listing pending before completed. Pure: the input list is never mutated. This drives the time-ordered agenda in `build_daily_view()`.
- **`Schedule.prioritize()`** — sorts fixed-time tasks and higher priorities first, breaking ties by earliest `start_time`, and sinks completed tasks to the bottom so the day leads with what's left. This drives the reasoning-annotated `build_priority_view()`.

### Filtering behavior

- **`Schedule.filter(pet=..., pet_name=..., status=...)`** — returns tasks matching any combination of a specific pet (by identity), a pet name (all pets sharing that name match), and completion status (`"pending"`, `"complete"`, or `None` for all). Pure and composable — e.g. `schedule.by_time(schedule.filter(pet_name="Rex", status="pending"))`.
- **`Schedule.active_for_day()`** — filters down to only the tasks whose recurrence places them on the schedule's `day` (delegates to `Activity.occurs_on()`).
- **`Pet.pending_activities()`** — a per-pet convenience filter returning that pet's not-yet-complete tasks.

### Conflict detection logic

- **`Activity.overlaps(other)`** — the primitive: two tasks overlap when each starts before the other ends (using `Activity.end_time`, derived from `start_time` + `duration_minutes`).
- **`Schedule.detect_conflicts()`** — read-only, returns every overlapping pair. A time-ordered sweep tracks the running set of still-active tasks so each task is compared against *all* earlier overlapping tasks, not just its immediate predecessor. Never mutates.
- **`Schedule.conflicts_by_pet()`** — classifies each overlapping pair as `same_pet` (impossible for one pet to honor — it can't be two places at once) or `cross_pet` (only competes for the owner's time). Builds on `detect_conflicts()` so the overlap logic lives in one place.
- **`Schedule.conflict_warning()`** — a never-raising, printable summary: `""` when nothing overlaps, otherwise one `⚠` line per clashing pair with same-pet conflicts listed first.
- **`Schedule.resolve_conflicts()`** — the only conflict method that mutates: pushes a movable (non-`is_fixed`) task that overlaps an earlier one to start when that earlier task ends, as long as it stays within the task's `latest` bound. Fixed tasks never move.

### Recurring task logic

- **`Activity.next_occurrence()`** — builds the next instance of a recurring task: `daily` advances the `start_date` by one day, `weekly` by seven; `once` (and any other frequency) returns `None`. Pure — the original task is not mutated, and the clone starts pending and detached from any pet/schedule.
- **`Activity.occurs_on(day)`** — decides whether a task appears on a given date: `daily` always occurs, `weekly` recurs on the weekday of its `start_date`, `once` occurs only on its `start_date`, and a task with no `start_date` always occurs (so simple demos still show every task).
- **`Schedule.complete(activity)`** — marks a task done and, for `daily`/`weekly` tasks, auto-schedules the next instance via `next_occurrence()`, attaching it to the same pet and this schedule. Returns the new instance, or `None` for non-recurring tasks.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
