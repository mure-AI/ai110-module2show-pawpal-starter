# PawPal+ Project Reflection

## 1. System Design
• Add a pet with a name
• Add actions needed to be taken on each pet (feeding, walks, medication appointment) and the time constraints or frequency
• View schedule for the day

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- ANSWER: My UML diagram included 4 main classes: User, Pet, Action, and Schedule. The User owns many pets and a pet has multiple activities which are part of a schedule created by the Schedule class. And finally the User owns or has the main schedule, which is created by the Schedule class. The Pet class is responsible for storing information about each pet, such as its name, activity and a filtered view of its own schedule. It also has a method to add more activities. The Action class handles the various actions that needed to be taken for each pet, including feeding, walks, and medication appointments, along with their associated time constraints or frequencies. The Scheduler class is responsible for managing the overall schedule, ensuring that all actions were organized and displayed correctly for the day.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

- My coding assistant suggested I store constraints and preferences as dictionary objects because nothing was being done with them in my original design. It also pointed out that multiple classes are affecting my activitiy list and suggested I give the authoritative power to only my Schedule object.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

- ANSWER: My scheduler considers start time, a numeric priority, whether a task is fixed (like a vet appointment that can't move), an earliest/latest window a task can slide within, and recurrence (daily/weekly/once). I decided fixed time mattered most because a fixed appointment is a hard commitment the owner can't reschedule, so nothing else is allowed to bump it. After that comes priority, then the earlier start time as a tiebreaker. Movable tasks only shift within their latest bound, so a preference never overrides a hard constraint.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- It redoes the same work more than once instead of saving it. What I mean is that everyday the build_daily_view method runs, it checks for time conflicts twice. I chose this because its a small app and a user can only have a handful of pets so I decided to use code that is easier to understand and safer to use because sorting a short list a few extra times is so fast and won't be noticed.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

- Which AI coding assistant features were most effective for building your scheduler?

- ANSWER: The most effective feature was being able to paste my UML and talk through the design before writing any code. Having the assistant read my whole file for context and point out design smells (like too many classes touching the activity list) caught problems early. Inline edits and quick refactors were also useful once I knew what change I wanted.

- How did using separate chat sessions for different phases help you stay organized?

- ANSWER: Keeping design, implementation, and testing in separate sessions meant each chat stayed focused on one job, so the assistant wasn't confusing my design questions with debugging. It also gave me a cleaner record to look back on for each phase, and I could restart a session if it went down the wrong path without losing my design decisions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.

- ANSWER: The assistant suggested caching the conflict-detection results so build_daily_view wouldn't recompute them. I modified that suggestion and left the recomputation in, because adding a cache meant extra state to keep in sync for a list that only ever has a handful of items. Keeping the logic simple and re-running it was cleaner and safer than optimizing something the user would never notice.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

- ANSWER: I tested marking a task complete, adding a task to a pet, sorting tasks by time (including unscheduled ones sorting to the bottom), recurrence (a completed daily task spawns the next day while a "once" task spawns nothing), and conflict detection (overlapping times are flagged, but back-to-back times where one ends exactly when the next starts are not). These were important because sorting, recurrence, and conflict detection are the core of the scheduler — if any of them is wrong the daily plan is wrong, and the back-to-back case in particular is an easy off-by-one to get wrong.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

- ANSWER: I'm fairly confident for the common cases, since the sorting, recurrence, and conflict logic all have passing tests. With more time I'd test conflict resolution itself (that a movable task actually gets pushed to the right time and stays within its latest bound), a task that can't be moved because there's no room, weekly recurrence landing on the right weekday, and cross-pet vs same-pet conflict labeling.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

- ANSWER: I'm most satisfied with the conflict handling. It doesn't just flag overlaps — it separates same-pet conflicts (which are impossible to honor) from cross-pet ones, then tries to resolve movable tasks automatically while leaving fixed ones alone. It felt like the scheduler was actually reasoning about the day rather than just listing tasks.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

- ANSWER: I'd actually use the owner's constraints and preferences, which I store but never read from during scheduling. I'd feed them into the ordering so the plan reflects the owner's real habits (like no walks before 7am), and I'd let conflict resolution try moving a task earlier or into its earliest/latest window instead of only pushing it back.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

- ANSWER: The biggest thing I learned is to give one part of the system clear authority over shared data. Early on multiple classes were all touching the activity list, and once I made the Schedule the single source of truth the whole design got easier to reason about and test. Working with AI, I learned it's great at spotting that kind of design smell, but I still have to be the one to decide whether its fix fits the app.

---

## 6. Being the Lead Architect with AI

- ANSWER: The most important thing I learned is that the AI is a fast, capable builder, but I'm the architect — I own the design decisions and it doesn't. It could generate clean code and flag smells quickly, but it had no sense of what "clean" meant for *this* app, so it would happily add complexity (like caching) that I had to reject. My job was to set the direction (one source of truth, keep it simple for a small app), give it enough context to be useful, and verify every suggestion against my own goals and my tests before accepting it. The AI made me faster, but it never made the decisions — being lead architect meant staying the one who decides what belongs and why.
