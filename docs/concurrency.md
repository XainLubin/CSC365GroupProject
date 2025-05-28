# Concurrency Control Analysis

### 1. Lost Update Phenomenon

**Scenario**: Student using two different devices or sessions to simultaneously update their course plan for the same quarter.

**Problem**: When two transactions modify the same student's planned courses concurrently, one transaction's changes can be completely lost when the second transaction overwrites the planning data without seeing the first transaction's modifications.

#### Sequence Diagram

```
Mobile Browser (T1)            Database                    Laptop Browser (T2)
     |                            |                              |
     |---- BEGIN TRANSACTION ---->|                              |
     |                            |<---- BEGIN TRANSACTION ----- |
     |                            |                              |
     |-- SELECT planned courses --|                              |
     |    (student_id=1,          |                              |
     |     quarter='2025-SPRING') |                              |
     |<-- [CSC 430, CSC 445] -----|                              |
     |                            |-- SELECT planned courses ----|
     |                            |    (student_id=1,            |
     |                            |     quarter='2025-SPRING')   |
     |                            |---- [CSC 430, CSC 445] ----->|
     |                            |                              |
     |-- INSERT CSC 357 --------->|                              |
     |    (student adds course    |                              |
     |     via mobile browser)    |                              |
     |                            |<-- DELETE CSC 445 -----------|
     |                            |    (student removes course   |
     |                            |     via laptop browser)      |
     |                            |<-- INSERT CSC 349 -----------|
     |                            |    (student adds different   |
     |                            |  course via laptop browser)  |
     |                            |                              |
     |---- COMMIT --------------->|                              |
     |                            |<---- COMMIT -----------------|
     |                            |                              |
     
Final state: [CSC 430, CSC 357, CSC 349]
Just T1: [CSC 430, CSC 445, CSC 357]
Just T2: [CSC 430, CSC 349]
```

---

### 2. Dirty Read Phenomenon  

**Scenario**: GPA calculation reads uncommitted grade changes from concurrent course completion transaction.

**Problem**: A transaction reads data that has been modified by another transaction that hasn't committed yet, leading to calculations based on potentially invalid data.

#### Sequence Diagram

```
Grade Update (T1)              Database                GPA Calculation (T2)
     |                            |                              |
     |---- BEGIN TRANSACTION ---->|                              |
     |                            |<---- BEGIN TRANSACTION ----- |
     |                            |                              |
     |-- UPDATE completed_courses |                              |
     |   SET grade='A'            |                              |
     |   WHERE student_id=1       |                              |
     |   AND course_id=349        |                              |
     |   (CSC 349: F -> A)        |                              |
     |                            |                              |
     |   Grade changed but        |                              |
     |   not committed yet        |                              |
     |                            |                              |
     |                            |-- SELECT grades for ---------|
     |                            |   student_id=1               |
     |                            |---- RETURNS UNCOMMITTED ---->|
     |                            |     grade 'A' for CSC 349    |
     |                            |                              |
     |                            |                              |-- Calculates GPA
     |                            |                              |   with 'A' grade
     |                            |                              |   (GPA = 3.17)
     |                            |                              |
     |                            |<-- INSERT academic_record ---|
     |                            |    (overall_gpa=3.17,        |
     |                            |    standing='Good Standing') |
     |                            |                              |
     |                            |<---- COMMIT -----------------|
     |                            |                              |
     |-- More grade updates ------|                              |
     |   SET grade='C'            |                              |
     |   (instructor changes      |                              |
     |    mind: A -> C)           |                              |
     |                            |                              |
     |---- COMMIT --------------->|                              |
     |                            |                              |
     
Final state: Academic record shows GPA=3.17 based on grade 'A'
Actual state: Student's grade is 'C', so GPA should be lower
```

---

### 3. Non-Repeatable Read Phenomenon

**Scenario**: Course planning transaction gets inconsistent results when checking unit limits across multiple queries.

**Problem**: Within a single transaction, reading the same data multiple times returns different results due to concurrent modifications, leading to inconsistent decision making.

#### Sequence Diagram

```
Course Planning (T1)           Database              Concurrent Planning (T2)
     |                            |                              |
     |---- BEGIN TRANSACTION ---->|                              |
     |                            |<---- BEGIN TRANSACTION ----- |
     |                            |                              |
     |-- SELECT SUM(units) ------>|                              |
     |   FROM planned_courses     |                              |
     |   WHERE student_id=1       |                              |
     |   AND quarter='2025-SPRING'|                              |
     |<-- 12 units ---------------|                              |
     |                            |                              |
     |    Check if we can add     |                              |
     |    CSC 430 (4 units)       |                              |
     |   12 + 4 = 16 units -> OK  |                              |
     |                            |                              |
     |                            |<-- INSERT planned_courses ---|
     |                            |    (student_id=1,            |
     |                            |     course_id=357,           |
     |                            |     quarter='2025-SPRING')   |
     |                            |     CSC 357: 4 units         |
     |                            |                              |
     |                            |<---- COMMIT -----------------|
     |                            |                              |
     |-- INSERT CSC 430 --------->|                              |
     |   (proceeds with original  |                              |
     |    plan to add course)     |                              |
     |                            |                              |
     |-- SELECT SUM(units) ------>|                              |
     |   (re-checking total)      |                              |
     |<-- 20 units ---------------|                              |
     |                            |                              |
     |   The same query now       |                              |
     |   Returns 20 units         |                              |
     |   Exceeds the 16 limit     |                              |
     |                            |                              |
     |---- COMMIT --------------->|                              |
     |                            |                              |
     
Final state: Student has 20 units planned (exceeds 16-unit limit)
```

---

## Isolation Level Solutions

### Use Isolation Level: SERIALIZABLE

**Prevents All Three Phenomena**: 
   - **Lost Updates**: Prevents concurrent modifications to the same planning data
   - **Dirty Reads**: Ensures GPA calculations only see committed grade changes  
   - **Non-Repeatable Reads**: Guarantees consistent unit amounts throughout planning transactions

### Alternatively: Advisory Locks

Advisory locks would allow us to prevent concurrent access on a per student basis rather than utilizing full transaction isolation. This would allow:

- Each student's course planning would be protected from concurrent modifications
- Other students could still plan courses simultaneously without blocking each other
- Better performance than utilizing SERIALIZABLE