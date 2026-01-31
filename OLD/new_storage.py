def main():
    import sqlite3

    DB_FILE = "YGO.db"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    ID = int(input("Enter Storage ID: "))
    
    cursor.execute("SELECT id FROM Storage WHERE id = ?", (ID,))
    if cursor.fetchone():
        print("Storage already exists!")
        return
        

    color = input("Enter Storage color: ")
    stor_type = input("Enter type of Storage: ")

    cursor.execute('''
    INSERT INTO Storage (id, color, type) VALUES (?, ?, ?)
    ''', (
        ID,
        color,
        stor_type,
    ))

    conn.commit()

    print(f"\nNew Storage entry with id {ID} created successfully.")
    return


if __name__ == "__main__":
	main()