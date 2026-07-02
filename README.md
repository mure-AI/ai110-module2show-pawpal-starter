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

## ✨ Features

The algorithms implemented in [pawpal_system.py](pawpal_system.py) (see [Smarter Scheduling](#-smarter-scheduling) for method-level detail):

- **Sorting by time** — orders tasks chronologically, pushing unscheduled tasks to the bottom and completed ones last.
- **Priority ordering** — ranks by fixed-time first, then higher priority, then earliest start time, sinking completed tasks.
- **Conflict detection** — a time-ordered sweep that flags *every* overlapping pair of tasks, not just adjacent ones.
- **Same-pet vs. cross-pet conflicts** — separates overlaps a single pet can't honor from ones that only compete for the owner's time.
- **Conflict warnings** — a readable ⚠ summary listing each clashing pair, same-pet conflicts first.
- **Automatic conflict resolution** — pushes movable tasks to start when the previous one ends (respecting each task's `latest` bound); fixed tasks never move.
- **Daily & weekly recurrence** — completing a recurring task auto-spawns its next instance (+1 day / +7 days); `once` tasks spawn nothing.
- **Day-aware filtering** — shows only the tasks that occur on a given day (daily always, weekly by weekday, once on its exact date).
- **Filter by pet & status** — composable filtering by pet identity, pet name, or pending/complete status.
- **Two plan views** — a time-ordered daily agenda and a priority-ordered plan that explains why each task is placed where it is.

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

### What you can do in the app

The Streamlit UI ([app.py](app.py)) is a single interactive page:

- **Enter owner & pet info** — set the owner name, pet name, and species (dog / cat / other).
- **Add tasks** — for each task, enter a title, duration (minutes), priority (low / medium / high), and start time, then click **Add task**. Added tasks appear in a running table.
- **Pick a view** — toggle between **By time (daily agenda)** and **By priority (with reasoning)**.
- **Generate the schedule** — click **Generate schedule** to run the tasks through the `Schedule` brain and render the organized plan.

### Example workflow

1. Set the owner to `Jordan` and the pet to `Mochi` (a dog).
2. Add **Morning walk** — 20 min, high priority, 08:00 — and click **Add task**.
3. Add **Breakfast** — 15 min, high priority, 08:00 — a second task at the *same* time.
4. Add **Litter cleanup** — 10 min, low priority, 12:00.
5. Choose **By time (daily agenda)** and click **Generate schedule**.
6. Read today's schedule: tasks come back time-ordered in an `st.table`, with a conflict banner above it.

### Scheduler behaviors on display

- **Sorting** — `Schedule.by_time()` returns the tasks chronologically (or `Schedule.prioritize()` in the priority view), so they render in order regardless of the order you added them.
- **Conflict warnings** — the two 08:00 tasks overlap, so `Schedule.conflict_warning()` surfaces an `st.warning`; a clash-free plan shows an `st.success` instead. Overlapping rows are flagged with a ⚠️ in the table.
- **Auto-resolution** — `Schedule.resolve_conflicts()` nudges movable tasks to start when the previous one ends (fixed tasks stay put).
- **Reasoning** — the *Why* column comes from the Scheduler's own `_explain()`, noting fixed time, priority, and frequency.
- **Summary** — a caption reports totals: tasks, pets, and done-vs-remaining counts.

### Sample CLI output

Running the terminal demo exercises the same `Schedule` logic without Streamlit:

```bash
python main.py
```

```
Tasks as added (insertion order):
  ○ 18:00 Evening medication (Rex, 10m, p3)
  ○ 08:00 Breakfast (Luna, 15m, p3)
  ✓ 07:30 Morning walk (Rex, 30m, p2)
  ○ 12:00 Litter cleanup (Luna, 10m, p1)
  ○ 08:00 Breakfast (Rex, 15m, p3)

Sorted by time (by_time):
  ✓ 07:30 Morning walk (Rex, 30m, p2)
  ○ 08:00 Breakfast (Luna, 15m, p3)
  ○ 08:00 Breakfast (Rex, 15m, p3)
  ○ 12:00 Litter cleanup (Luna, 10m, p1)
  ○ 18:00 Evening medication (Rex, 10m, p3)

Pending only (filter status='pending'):
  ○ 08:00 Breakfast (Luna, 15m, p3)
  ○ 08:00 Breakfast (Rex, 15m, p3)
  ○ 12:00 Litter cleanup (Luna, 10m, p1)
  ○ 18:00 Evening medication (Rex, 10m, p3)

Complete only (filter status='complete'):
  ✓ 07:30 Morning walk (Rex, 30m, p2)

Rex's tasks (filter pet_name='Rex'):
  ✓ 07:30 Morning walk (Rex, 30m, p2)
  ○ 08:00 Breakfast (Rex, 15m, p3)
  ○ 18:00 Evening medication (Rex, 10m, p3)

Luna's pending tasks (filter pet_name='Luna', status='pending'):
  ○ 08:00 Breakfast (Luna, 15m, p3)
  ○ 12:00 Litter cleanup (Luna, 10m, p1)

Conflict check (conflict_warning):
1 scheduling conflict found:
  ⚠ different pets: Breakfast (08:00) overlaps Breakfast (08:00)

PawPal+ plan — Wednesday, July 1, 2026
──────────────────────────────────────
  07:30 – 08:00   Morning walk         Rex    exercise  ✓ done
  08:00 – 08:15   Breakfast            Luna   feeding   ★ high  ⚠ conflict
  08:00 – 08:15   Breakfast            Rex    feeding   ★ high  📌 fixed  ⚠ conflict
  12:00 – 12:10   Litter cleanup       Luna   hygiene 
  18:00 – 18:10   Evening medication   Rex    health    ★ high  📌 fixed
──────────────────────────────────────
  5 tasks across 2 pets · 1 done, 4 to go

Verify: two tasks at the same time
1 scheduling conflict found:
  ⚠ same pet (Milo): Feed (09:00) overlaps Vet call (09:00)
  ✓ Scheduler correctly identified the conflict
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
