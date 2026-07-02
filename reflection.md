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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- It redoes the same work more than once instead of saving it. What I mean is that everyday the build_daily_view method runs, it checks for time conflicts twice. I chose this because its a small app and a user can only have a handful of pets so I decided to use code that is easier to understand and safer to use because sorting a short list a few extra times is so fast and won't be noticed.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
