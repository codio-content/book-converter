Thus, we concentrate on Agile in the six software development chapters in Part II of the book,  but each chapter also gives the perspective of the Plan-and-Document methodologies on topics like requirements, testing, project management, and maintenance. This contrast allows readers to decide for themselves when each methodology is appropriate.

While we now see how to build some software successfully, not all projects are small. We next show how to design software to enable composition into services like Amazon.com.

---
**Summary:** In contrast to the Plan-and-Document lifecycles, the Agile lifecycle works with customers to continuously add features to working prototypes until the customer is satisfied, allowing customers to change what they want as the project develops. Documentation is primarily through user stories and test cases, and it does not measure progress against a predefined plan. Progress is gauged instead by recording ___velocity___, which essentially is the rate that a project completes features.

---



|||challenge
True or False: A big difference between Spiral and Agile development is building prototypes and interacting with customers during the process. 
<details><summary>Check yourself</summary>False: Both build working but incomplete prototypes that the customer helps evaluate. The difference is that customers are involved every two weeks in Agile versus up to two years in with Spiral.</details>
|||

## Versions of Agile
There is not just a single Agile lifecycle. We are following ___Extreme Programming___ (XP), which includes one- to two-week iterations, behavior driven design (see Chapter chap:bdd), test-driven development (see Chapter chap:tdd), and pair programming (see Section sec:Pair). Another popular version is ___Scrum___ (see Section sec:Scrum), where self-organizing teams use two- to four-week iterations called ___sprints___, and then regroup to plan the next sprint. A key feature is daily standup meetings to identify and overcome obstacles. While there are multiple roles in the scrum team, the norm is to rotate the roles over time. The ___Kanban___ approach is derived from Toyota's just-in-time manufacturing process, which in this case treats software development as a pipeline. Here the team members have fixed roles, and the goal is to balance the number of team members so that there are no bottlenecks with tasks stacking up waiting for processing. One common feature is a wall of cards that to illustrate the state of all tasks in the pipeline. There are also hybrid lifecycles that try to combine the best of two worlds. For example, ___ScrumBan___ uses the daily meetings and sprints of Scrum but replaces the planning phase with the more dynamic pipeline control of the wall of cards from Kanban.
## Reforming Acquisition Regulations
Long before the ACA website, there were calls to reform software acquisition, as in this US National Academies study of the Department of Defense (DOD):

“The DOD is hampered by a culture and acquisition-related practices that favor large programs, high-level oversight, and a very deliberate, serial approach to development and testing (the waterfall model). Programs that are expected to deliver complete, nearly perfect solutions and that take years to develop are the norm in the DOD... These approaches run counter to Agile acquisition practices in which the product is the primary focus, end users are engaged early and often, the oversight of incremental product development is delegated to the lowest practical level, and the program management team has the flexibility to adjust the content of the increments in order to meet delivery schedules... Agile approaches have allowed their adopters to outstrip established industrial giants that were beset with ponderous, process-bound, industrial-age management structures. Agile approaches have succeeded because their adopters recognized the issues that contribute to risks in an IT program and changed their management structures and processes to mitigate the risks.”

(national2010Achieving)

Even President Obama belatedly recognized the difficulties of software acquisition.  On November 14, 2013, he said in a speech: “... when I do some Monday morning quarterbacking on myself, one of the things that I do recognize is since I know how we purchase technology in the federal government is cumbersome, complicated and outdated ...  it's part of the reason why, chronically, federal IT programs are over budget, behind schedule... since I [now] know that the federal government has not been good at this stuff in the past, two years ago as we were thinking about this... we might have done more to make sure that we were breaking the mold on how we were going to be setting this up.”
