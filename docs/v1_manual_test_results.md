# Example workflow
Basic student creation and course planning flow:
1. Create a new student account
2. Login with the created account
3. Get student details
4. Plan a course for a future quarter
5. View the generated course plan
6. Get course details by ID and code

# Testing results

1. Create a new student:
```bash
curl -X 'POST' \
  'https://course-finder.onrender.com/students/create' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "first_name": "John",
  "last_name": "Doe",
  "email": "jdoe@calpoly.edu",
  "password": "password123",
  "major_id": 1
}'
```
Response:
```json
{
  "id": 1
}
```

2. Login with the created account:
```bash
curl -X 'POST' \
  'https://course-finder.onrender.com/login/jdoe@calpoly.edu?password=password123' \
  -H 'accept: application/json'
```
Response:
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "jdoe@calpoly.edu",
  "major_id": 1
}
```

3. Get student details:
```bash
curl -X 'GET' \
  'https://course-finder.onrender.com/students/1' \
  -H 'accept: application/json'
```
Response:
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "jdoe@calpoly.edu",
  "major_id": 1,
  "completed_courses": [],
  "planned_courses": []
}
```

4. Plan a course:
```bash
curl -X 'POST' \
  'https://course-finder.onrender.com/plan_course?student_id=1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "course_id": 1,
  "planned_quarter": "Fall 2025"
}'
```
Response: 204 No Content

5. View course plan:
```bash
curl -X 'GET' \
  'https://course-finder.onrender.com/planner/create_course_plan?student_id=1' \
  -H 'accept: application/json'
```
Response:
```json
{
  "quarters": [
    {
      "quarter_name": "Fall 2025",
      "courses": [
        {
          "id": 1,
          "department_code": "CSC",
          "course_number": 101,
          "units": 4,
          "title": "Introduction to Programming",
          "description": "Basic programming concepts"
        }
      ]
    },
    {
      "quarter_name": "Winter 2026",
      "courses": []
    },
    {
      "quarter_name": "Spring 2026",
      "courses": []
    },
    {
      "quarter_name": "Fall 2026",
      "courses": []
    }
  ]
}
```

6. Get course by ID:
```bash
curl -X 'GET' \
  'https://course-finder.onrender.com/courses/1' \
  -H 'accept: application/json'
```
Response:
```json
{
  "id": 1,
  "department_code": "CSC",
  "course_number": 101,
  "units": 4,
  "title": "Introduction to Programming",
  "description": "Basic programming concepts"
}
```

7. Get course by code:
```bash
curl -X 'GET' \
  'https://course-finder.onrender.com/courses/code/CSC/101' \
  -H 'accept: application/json'
```
Response:
```json
{
  "id": 1,
  "department_code": "CSC",
  "course_number": 101,
  "units": 4,
  "title": "Introduction to Programming",
  "description": "Basic programming concepts"
}
``` 