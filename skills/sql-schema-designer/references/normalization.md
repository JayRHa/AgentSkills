# Normalization Reference

Normalization removes redundancy so each fact is stored once, eliminating update, insert, and delete anomalies. Target **3NF** by default; most well-keyed 3NF tables are also BCNF.

## The anomalies you are preventing

Given a denormalized `orders` table holding customer name + product name per row:
- **Update anomaly:** renaming a customer requires updating every order row.
- **Insert anomaly:** you cannot record a new product until someone orders it.
- **Delete anomaly:** deleting the last order for a customer erases the customer's details.

## First Normal Form (1NF)

Rule: atomic values, no repeating groups, no arrays/CSV in a column, a key exists.

Violation:
```
student(id, name, courses)
1, Ada, "Math,Physics,CS"
```
Fix — extract repeating group into its own row/table:
```
student(id, name)
enrollment(student_id, course)   -- one row per course
```

## Second Normal Form (2NF)

Applies when the PK is composite. Rule: no non-key attribute depends on only **part** of the key.

Violation — PK is (order_id, product_id) but `product_name` depends only on `product_id`:
```
order_item(order_id, product_id, product_name, quantity)
```
Fix — move the partial-dependency attribute to where its determinant is the whole key:
```
order_item(order_id, product_id, quantity)
product(product_id, product_name)
```

## Third Normal Form (3NF)

Rule: no non-key attribute depends on another non-key attribute (no transitive dependency).

Violation — `dept_name` depends on `dept_id`, which is not the key `employee_id`:
```
employee(employee_id, name, dept_id, dept_name)
```
Fix:
```
employee(employee_id, name, dept_id)
department(dept_id, dept_name)
```

Mnemonic: every non-key attribute depends on **the key, the whole key, and nothing but the key**.

## Boyce-Codd Normal Form (BCNF)

Stricter 3NF: for every functional dependency X -> Y, X must be a candidate key. Catches anomalies when a non-prime attribute determines part of a candidate key (overlapping candidate keys).

Violation — each subject has exactly one teacher, but PK is (student, subject):
```
teaches(student, subject, teacher)
-- FD: teacher -> subject  (teacher is not a candidate key)
```
Fix:
```
teacher_subject(teacher, subject)   -- teacher PK
student_teacher(student, teacher)
```

## When to stop / when to denormalize

- Stop at 3NF unless you can name a concrete remaining anomaly (then go BCNF).
- 4NF/5NF matter only with independent multi-valued facts in one table; usually solved by splitting into separate junction tables.
- Denormalize only after: (a) the normalized schema exists, (b) a real read query is measurably too slow, and (c) you define a consistency mechanism (trigger / application write / materialized view) and an acceptable staleness window.

## Decomposition checklist

- [ ] No column stores lists, CSV, or repeating groups (1NF).
- [ ] Every table has a stable primary key.
- [ ] With a composite PK, no attribute depends on only part of it (2NF).
- [ ] No non-key attribute depends on another non-key attribute (3NF).
- [ ] Every determinant is a candidate key (BCNF) — or the exception is documented.
- [ ] Decompositions are lossless (you can rejoin to the original) and dependency-preserving.
- [ ] Intentional snapshots (sale price, document name) are documented as point-in-time facts, not flagged as redundancy.
