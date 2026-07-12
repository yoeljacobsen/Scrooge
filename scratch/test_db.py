import sys
import os

# Adjust path to import from check folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../check')))
import scrooge

# Load the database program code
db_code_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../programs/sql_db.sg'))
with open(db_code_path) as f:
    db_code = f.read()

# Scrooge test script:
# 1. Initialize a database.
# 2. CREATE TABLE users (id=10, score=20) -> table_id 0.
# 3. INSERT three rows: (1, 95), (2, 80), (3, 95).
# 4. SELECT id FROM users WHERE score = 95.
test_snippet = """
10 hnew -> [ db ] [
  { Step 1: Create table with columns [ 10 20 ] at table_id 0 }
  [ 10 20 ] nil cons 0 $ cons 1 $ cons -> [ create_stmt ] [
    db create_stmt db_create_table
  ]

  { Step 2: Insert row 1 [ 1 95 ] }
  [ 1 95 ] nil cons 0 $ cons 2 $ cons -> [ insert_stmt1 ] [
    db insert_stmt1 db_insert
  ]

  { Step 3: Insert row 2 [ 2 80 ] }
  [ 2 80 ] nil cons 0 $ cons 2 $ cons -> [ insert_stmt2 ] [
    db insert_stmt2 db_insert
  ]

  { Step 4: Insert row 3 [ 3 95 ] }
  [ 3 95 ] nil cons 0 $ cons 2 $ cons -> [ insert_stmt3 ] [
    db insert_stmt3 db_insert
  ]

  { Step 5: Select projected column [ 10 ] (id) where column 20 (score) = 95 }
  95 nil cons 20 $ cons [ 10 ] $ cons 0 $ cons 3 $ cons -> [ select_stmt ] [
    db select_stmt db_select
  ]
]
"""

full_code = db_code + "\n" + test_snippet

print("==========================================================")
print("PROVING RUNTIME CORRECTNESS OF THE SCROOGE SQL DATABASE")
print("==========================================================")
print("SQL Statements executed:")
print("  - CREATE TABLE users (id INT, score INT)")
print("  - INSERT INTO users VALUES (1, 95)")
print("  - INSERT INTO users VALUES (2, 80)")
print("  - INSERT INTO users VALUES (3, 95)")
print("  - SELECT id FROM users WHERE score = 95")
print("----------------------------------------------------------")

result = scrooge.run(full_code)
print("Execution succeeded!")
print("Final top-of-stack query results:", result[-1])
print("----------------------------------------------------------")

expected = [[3], [1]]
if result and result[-1] == expected:
    print("Verification: PASS (Results match expected values)")
    print("==========================================================")
    sys.exit(0)
else:
    print(f"Verification: FAIL (Expected {expected}, got {result})")
    print("==========================================================")
    sys.exit(1)
