Group Project: User Stories and Exceptions

Contributors:
        Jake Reese, 
        Matthew Dumag, 
        Xain Lubin, 
        Spencer Perley, 

User Stories for course mapping application:

1.  As a student Majoring in Computer Science, I want to input my completed courses and target degree path, so that I can generate an optimal course schedule that allows me to graduate in the shortest time possible.

2.  As a student interested in specializing in Data Science, I want to view the shortest path to complete my concentration requirements, so that I can plan my remaining semesters effectively and focus on courses that align with my desired career.

3.  As a student approaching graduation, I want to input my completed courses and browse the requirements of all degrees to see which degree(s) I am nearest to completing, so that I can apply for all degrees I meet the requirements for.

4.  As a student interested in multiple majors, I want to compare my progress toward each of them, so I can make a more informed decision.

5.  As an admin, I want to input and edit course and major information in the database, so the system is up to date with the program offerings and course plans.

6.  As an indecisive student, I want to save and load different course plans, so I can explore and compare various academic paths to graduation.


7.  As a student athlete, I want to exclude certain class days and times from my plan, so that I can generate a roadmap that fits my availability.

8.  As a transfer student, I want to enter my equivalent transfer credits, so that the system considers them in my roadmap.

9.  As a student double majoring, I want to generate a combined roadmap for two majors, so that I can understand the overlapping requirements and determine the feasibility of completing both.

10. As an academic advisor, I want to view and comment on a student’s roadmap, so I can guide their course selection and long-term planning.

11. As a student who has a child and a job, I want to be able to create a schedule with a maximum number of units per quarter.

12. As someone who is looking into school for the first time, and is not sure what degree will be best for the career I want to pursue, I want to input my career choice so that I can get the most efficient education plan to get the degree necessary for the position I want.


Exceptions:

1.  Missing Course Database Entry
        If a user inputs a course that is not found in the college’s database, the application will display an error message and ask the user to verify course details.

2.  Invalid Concentration Selection
        If a user selects a concentration not supported by their chosen major, an error message will be shown. The application will ask the user to choose an available concentration or provide a list of compatible concentrations

3.  Invalid User Input
        If a user enters invalid course information (e.g., non-existent course code), the system will give immediate feedback on the error and list of valid course codes. It will pause calculation of the shortest path until the proper course code is provided.

4.  Empty Course History
        If the user generates a roadmap without entering any completed courses, the system will assume an empty slate, but issue a warning that the completed course list is empty.

5.  No Valid Roadmap Found
        If the system is not able to find a path to graduation given the user’s input/constraints, it will explain the issue and prompt for a fix to the input.

6.  Time Conflict with User Constraints
        If the generated roadmap suggests a course at a time the user has marked unavailable, the system will flag the conflict and offer alternatives or let the user revise the constraints.

7.  Course Prerequisite Not Met
        If the user selects a course for a future term without completing its prerequisite, the system will automatically arrange correct the plan or alert the issue about the conflict.

8.  Incompatible Double Major Selection
        If the user selects two majors with conflicting requirements, the system will alert the user and suggest more compatible pairings.

9.  Cyclic Prerequisite Detection in Database
        If a cycle is detected in prerequisite chains, the system will prevent roadmap generation including the chain, and will notify the admin to fix the loop.

10. Unselected Major
        If a user attempts to generate a roadmap without choosing a major or concentration, the application will stop and prompt them to select a major before proceeding.
11. Exceeded Unit Limit per Quarter
        If the generated roadmap exceeds the user’s defined maximum unit load per quarter, the system will issue a warning and prompt the user to adjust preferences or allow it to automatically rebalance the plan.
12. Backend/API Failure
        If course data or roadmap generation fails to a server side or API error, the system will display a user friendly error message and allow the user to retry or save their current progress.
