import pymysql
import re

try:
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='123456',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.Cursor
    )
    
    cursor = conn.cursor()
    
    # Read SQL file
    with open('english_app.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split by DELIMITER
    delimiter = ';'
    statements = []
    current_statement = ''
    
    for line in sql_content.split('\n'):
        # Check for DELIMITER directive
        if line.strip().startswith('DELIMITER'):
            delimiter = line.split()[1]
            continue
        
        current_statement += line + '\n'
        
        # Check if statement ends with current delimiter
        if line.rstrip().endswith(delimiter):
            # Remove the delimiter from the end
            statement = current_statement.rstrip()[:-len(delimiter)].strip()
            if statement:
                statements.append(statement)
            current_statement = ''
            delimiter = ';'  # Reset to default
    
    # Execute statements
    for i, statement in enumerate(statements):
        if statement.strip():
            try:
                cursor.execute(statement)
                print(f"✓ Statement {i+1} executed")
            except Exception as e:
                print(f"✗ Statement {i+1} failed: {e}")
                print(f"  SQL: {statement[:100]}...")
    
    conn.commit()
    print("\n✓ Database schema imported successfully!")
    
except Exception as e:
    print(f"✗ Error: {e}")
finally:
    cursor.close()
    conn.close()
