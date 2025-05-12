API Specification and Example Flows for Database Team Project

Endpoints:

POST /login/{username} {password}   //passes in a username and password and returns the stored information about the student 
POST /add_future_course/{courseID} // adds a course to the upcoming courses 
POST /add_completed_course/{courseID} // adds a course that has been completed 
POST  /complete_course/{courseID}  //marks the course as completed
GET   /create_course_plan/    //returns a list of courses that the user should take over the next quarters.
POST/ add_requirement/       // add a  requirements (ie A,B,C) and a count of these requirements
POST /set_preferences 
This sets the preferences of how many courses you want to take per quarter and what types of classes you want to take in terms of difficulty 
Avoid days of the week/ time slot
POST /mark_course_completed/{grade}  // marks a course as completed with a grade… 
GET /user/preferences // returns the users current scheduling constraints and preferences
GET /user/requirements   // returns the courses the student needs to fulfill their degree

Example Flows:

Jordan is a Computer Science major who has completed many of the introductory courses and wants to plan the most efficient path to graduation. He logs in, updates his academic history, sets preferences, and generates a course plan.
Jordan logs into the system by calling POST /login/Goatdan ******  to access the site
Jordan marks his previously completed courses by calling POST /add_completed_courses/CSC101 and POST /add_completed_courses/CSC202
Jordan then sets preferences for course load and availability by calling POST/set_preferences.
Jordan reviews his current preferences calling GET /user/preferences
Finally Jordan generates a course plan by calling GET /create_course_plan

Maya is a transfer student who needs to fulfill general education requirements to graduate. She wants to ensure she meets Cal Poly’s GE requirements. Maya logs in, adds her transfer credits, updates her requirements, and generates her course plan.
Maya logs in with POST/login/puppykicker **********
Maya adds the specific GE requirements by calling POST/add_requirment/GE_AREA_B
Maya adds a transferred course she previously completed by calling POST/add_completed_course/ENGL134
Maya completes a course and marks it without a grade calling POST/complete_course/PHIL230
Maya views her updated degree requirements calling GET/user/requirements.
Lastly, Maya generates a new course plan based on her updated progress calling GET/create_course_plan.

Steven is a third year student who has used the system before. He has just received his grades for the end of the quarter, and wants to update some ‘in-progress’ courses as completed.
Steven logs in with POST/login/scubasteve*******
Steven first adds the recently finished course to his completed courses with POST/add_completed_course/CSC203
Steven then updates the courses status with the grade (A) he received using POST/mark_course_completed/A
Steven adds a course he plans to take next quarter using POST/add_future_course/CSC349.
Steven retrieves his current preferences to review scheduling conflicts with GET/user/preferences.
Finally, Steven generates a new course plan based on his current and future courses using GET/create_course_plan.
