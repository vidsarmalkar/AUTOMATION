import os
import hashlib
import sys
import sqlite3


def create_database(dir_path: str):
    """Create current and previous tables in a database"""
    db_name = os.path.join(dir_path, 'watch.db')
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    create_table(cursor, "current")
    create_table(cursor, "previous")
    conn.commit()
    conn.close()


def create_table(cursor, table_name):
    """Create a table with the specified name"""
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_path TEXT NOT NULL UNIQUE,
            file_name TEXT NOT NULL,
            file_hash TEXT NOT NULL
        )
        """
    )


def compute_file_hash(file_path: str):
    """Compute hash of a given file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(8192)  # Read files in 8192 chunks
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_directory_hash(dir_path: str):
    """Compute hash for entire directory."""
    file_info = []
    for root, _, files in os.walk(dir_path):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            file_name = file
            # Ignore watch.db
            if file_name.lower() == 'watch.db':
                continue
            file_hash = compute_file_hash(full_path)
            file_info.append((full_path, file_name, file_hash))
    return file_info


def drop_table(cursor, table_name):
    """Drop a table with the specified name"""
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")


def update_current_db(dir_path, file_info):
    db_name = os.path.join(dir_path, 'watch.db')
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Move the current table data into previous
    drop_table(cursor, "previous")
    create_table(cursor, "previous")
    cursor.execute("""
        INSERT INTO previous (full_path, file_name, file_hash)
        SELECT full_path, file_name, file_hash
        FROM current
    """)
    
    drop_table(cursor, "current")
    create_table(cursor, "current")
    
    # Add data into current table
    cursor.executemany(f"""
        INSERT OR REPLACE INTO current (full_path, file_name, file_hash)
        VALUES (?, ?, ?)
    """, file_info)
    
    conn.commit()
    conn.close()


def compare(dir_path):
    """Compare current and previous table. If different, return true."""
    db_name = os.path.join(dir_path, 'watch.db')
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""SELECT full_path, file_hash FROM current EXCEPT SELECT full_path, file_hash FROM previous;""")
    rows = cursor.fetchall()
    conn.close()
    return len(rows) > 0


def main():
    arguments = sys.argv
    # Select the directory path
    if len(arguments) >= 2:
        dir_path = arguments[1]
        # Create database
        create_database(dir_path)
        # Calculate hash
        file_info = compute_directory_hash(dir_path)
        
        db_name = os.path.join(dir_path, 'watch.db')
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""SELECT COUNT(*) FROM current;""")
        rows = cursor.fetchall()
        
        if rows[0][0] == 0:
            # Just add data into current
            print("This is first run. Adding data into current.")
            cursor.executemany(f"""
                INSERT OR REPLACE INTO current (full_path, file_name, file_hash)
                VALUES (?, ?, ?)
            """, file_info)
            conn.commit()
            conn.close()
        else:
            # Update current and previous
            update_current_db(dir_path, file_info)
            is_changed = compare(dir_path)
            if is_changed:
                print('There are changes..')
            else:
                print('There are no changes from last run..')
    else:
        print('You need to provide directory path')


if __name__ == '__main__':
    main()
