import sys
import os

# Adjust path to import from check folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../check')))
import scrooge

# Load the database program code
db_code_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../programs/sql_db.sg'))
with open(db_code_path) as f:
    db_code = f.read()

# Scrooge snippet to run the JOIN test case:
test_snippet = """
10 hnew -> [ db ] [
  { Step 1: Create left table (id=0) with columns [ 10 20 ] (id, score) }
  [ 10 20 ] nil cons 0 $ cons 1 $ cons -> [ create_stmt1 ] [
    db create_stmt1 db_create_table
  ]

  { Step 2: Create right table (id=1) with columns [ 20 30 ] (score, grade_id) }
  [ 20 30 ] nil cons 1 $ cons 1 $ cons -> [ create_stmt2 ] [
    db create_stmt2 db_create_table
  ]

  { Step 3: Populate left table with 50 rows (id 1..50, score = id * 2) }
  db 0 1 50 2 populate_data

  { Step 4: Populate right table with 50 rows (score = id * 2, grade_id = 1000 + id) }
  db 1 1 50 populate_right_data

  { Step 5: Execute INNER JOIN and project Left [ 10 ] (id) and Right [ 30 ] (grade_id) }
  { join_stmt AST: [ 4 0 1 20 20 [ 10 ] [ 30 ] ] }
  [ 30 ] nil cons [ 10 ] $ cons 20 $ cons 20 $ cons 1 $ cons 0 $ cons 4 $ cons -> [ join_stmt ] [
    db join_stmt db_join
  ]
]
"""

full_code = db_code + "\n" + test_snippet

print("==========================================================")
print("PROVING RUNTIME CORRECTNESS OF THE SCROOGE SQL INNER JOIN")
print("==========================================================")
print("Populating 50 rows in Left Table (columns: [id, score])")
print("Populating 50 rows in Right Table (columns: [score, grade_id])")
print("Running INNER JOIN on score column...")
print("Projecting: [grade_id, id]")
print("----------------------------------------------------------")

result = scrooge.run(full_code)
print("Execution succeeded!")
joined_rows = result[-1]
print("Total joined rows returned:", len(joined_rows))
print("First row:", joined_rows[0] if joined_rows else None)
print("Last row:", joined_rows[-1] if joined_rows else None)
print("----------------------------------------------------------")

expected_count = 50
passed = True

if len(joined_rows) != expected_count:
    print(f"Verification: FAIL - Expected {expected_count} rows, got {len(joined_rows)}")
    passed = False
else:
    for idx, row in enumerate(joined_rows):
        expected_id = 50 - idx
        expected_grade = 1000 + expected_id
        if row != [expected_grade, expected_id]:
            print(f"Verification: FAIL - At index {idx}, expected {[expected_grade, expected_id]}, got {row}")
            passed = False
            break

if passed:
    print("Verification: PASS (All joined rows are correct)")
    print("==========================================================")
    sys.exit(0)
else:
    print("==========================================================")
    sys.exit(1)
