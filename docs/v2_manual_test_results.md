# Example workflows
Additional flows implemented in V2:
1. Major management flow
2. Course management flow
3. Course completion tracking flow
4. Requirements checking flow

# Testing results

## 1. Major Management Flow

1. Get all majors:
```bash
curl -X 'GET' \
  'https://course-finder.onrender.com/majors/' \
  -H 'accept: application/json'
```
Response:
```json
[
  {
    "id": 1,
    "name": "Computer Science",
    "description": "Computer Science major at Cal Poly"
  }
]
```

2. Get specific major:
```bash
curl -X 'GET' \
  'https://course-finder.onrender.com/majors/1' \
  -H 'accept: application/json'
```
Response:
```json
{
  "id": 1,
  "name": "Computer Science",
  "description": "Computer Science major at Cal Poly",
  "students": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "jdoe@calpoly.edu"
    }
  ]
}
```

3. Get students in major:
```bash
curl -X 'GET' \
  'https://course-finder.onrender.com/majors/1/students' \
  -H 'accept: application/json'
```
Response:
```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "jdoe@calpoly.edu"
  }
]
```

## 2. Course Management Flow

1. Get all courses:
```bash
curl -X 'GET' \
  'https://course-finder.onrender.com/courses/' \
  -H 'accept: application/json'
```
Response:
```json
[
  {
    "id": 1,
    "department_code": "CSC",
    "course_number": 101,
    "units": 4,
    "title": "Introduction to Programming",
    "description": "Basic programming concepts"
  }
]
```

2. Get course by code:
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

3. Get major courses:
```bash
curl -X 'GET' \
  'https://course-finder.onrender.com/courses/major/1' \
  -H 'accept: application/json'
```
Response:
```json
[
  {
    "id": 1,
    "department_code": "CSC",
    "course_number": 101,
    "units": 4,
    "title": "Introduction to Programming",
    "description": "Basic programming concepts",
    "is_required": true
  }
]
```

## 3. Course Completion Tracking Flow

1. Mark course as completed:
```bash
curl -X 'POST' \
  'https://course-finder.onrender.com/students/1/completed_courses' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "course_id": 1,
  "grade": "A",
  "quarter": "Fall 2024"
}'
```
Response: 204 No Content

2. View completed courses:
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
  "completed_courses": [
    {
      "course_id": 1,
      "grade": "A",
      "quarter": "Fall 2024"
    }
  ],
  "planned_courses": [
    {
      "course_id": 1,
      "planned_quarter": "Fall 2025"
    }
  ]
}
```

## 4. Requirements Checking Flow

1. Check major requirements:
```bash
curl -X 'GET' \
  'https://course-finder.onrender.com/planner/requirements?student_id=1' \
  -H 'accept: application/json'
```
Response:
```json
[
  {
    "id": 2,
    "department_code": "CSC",
    "course_number": 202,
    "units": 4,
    "title": "Data Structures",
    "description": "Advanced programming concepts"
  }
]
``` 