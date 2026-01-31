def create_db():
	import sqlite3
	from utils import config

	conn = sqlite3.connect(config().get("database"))
	cursor = conn.cursor()

	# Cards table
	cursor.execute('''
	CREATE TABLE IF NOT EXISTS Card (
	    id INTEGER PRIMARY KEY,
	    name TEXT NOT NULL,
	    type TEXT,
	    race TEXT,
	    level INTEGER,
	    atk INTEGER,
	    def INTEGER,
	    linkval INTEGER,
	    linkmarkers TEXT,
	    scale INTEGER,
	    attribute TEXT,
	    archetype TEXT,
	    desc TEXT
	)
	''')

	# CardSets table
	cursor.execute('''
	CREATE TABLE "Card_Set" (
	"card_id"	INTEGER NOT NULL,
	"set_code"	TEXT NOT NULL,
	"set_name"	TEXT NOT NULL,
	"set_rarity"	TEXT NOT NULL,
	PRIMARY KEY("set_code","set_rarity"),
	FOREIGN KEY("card_id") REFERENCES "Card"("id")
	);
	''')

	# CardImages table
	cursor.execute('''
	CREATE TABLE "Card_Image" (
		"card_id"	INTEGER NOT NULL UNIQUE,
		"image"	TEXT NOT NULL,
		PRIMARY KEY("card_id"),
		FOREIGN KEY("card_id") REFERENCES "Card"("id")
	)
	''')

	# Storage table
	cursor.execute('''
	CREATE TABLE "Storage" (
		"id"	INTEGER NOT NULL UNIQUE,
		"color"	TEXT NOT NULL,
		"type"	TEXT NOT NULL,
	    PRIMARY KEY("id")
	)
	''')

	# Card in Storage table
	cursor.execute('''
	CREATE TABLE "Card_in_Storage" (
		"card_code"	INTEGER NOT NULL,
		"storage_id"	INTEGER NOT NULL,
	    "page"	INTEGER NOT NULL,
		"count"	INTEGER NOT NULL,
		PRIMARY KEY("card_code","storage_id","page"),
		FOREIGN KEY("card_code") REFERENCES "Card_Set"("set_code"),
		FOREIGN KEY("storage_id") REFERENCES "Storage"("id")
	)
	''')
	conn.commit()

	print("Database created successfully.")
	return


def create_storage():
    import sqlite3
    from utils import config

    DB_FILE = config().get("database")

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


def transfer_card_in_storage():
    import sqlite3
    import questionary
    from utils import config

    DB_FILE = config().get("database")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # --- Step 1: card set ---
    set_id = input("Card set ID: ").upper()

    # --- Step 2: get storages ---
    cur.execute("""
        SELECT DISTINCT storage_id
        FROM Card_in_Storage
        WHERE card_code=?
    """, (set_id,))
    
    storages = [str(r[0]) for r in cur.fetchall()]

    if not storages:
        print("No cards found for that set_id")
        return

    from_storage = questionary.select(
        "Select storage:",
        choices=storages
    ).ask()

    # --- Step 3: get pages ---
    cur.execute("""
        SELECT page
        FROM Card_in_Storage
        WHERE card_code=? AND storage_id=?
    """, (set_id, from_storage))

    pages = [str(r[0]) for r in cur.fetchall()]

    from_page = questionary.select(
        "Select page:",
        choices=pages
    ).ask()

    # --- Step 4: amount ---
    move_amount = int(questionary.text("Amount to transfer:").ask())

    # --- Step 5: destination ---
    to_storage = questionary.text("Destination storage:").ask()
    to_page = questionary.text("Destination page:").ask()

    # --- Step 6: check count ---
    cur.execute("""
        SELECT count FROM Card_in_Storage
        WHERE card_code=? AND storage_id=? AND page=?
    """, (set_id, from_storage, from_page))

    current = cur.fetchone()[0]

    if move_amount > current:
        print("Not enough cards.")
        return

    # --- Step 7: transaction ---
    conn.execute("BEGIN")

    # subtract source
    cur.execute("""
        UPDATE Card_in_Storage
        SET count = count - ?
        WHERE card_code=? AND storage_id=? AND page=?
    """, (move_amount, set_id, from_storage, from_page))

    # add destination
    cur.execute("""
        INSERT INTO Card_in_Storage (card_code, storage_id, page, count)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(card_code, storage_id, page)
        DO UPDATE SET count = count + excluded.count
    """, (set_id, to_storage, to_page, move_amount))

    conn.commit()

    print("Transfer done.")

    conn.close()


def card_to_storage(card_code, storage_id, count, page):
    import sqlite3
    from utils import config

    DB_FILE = config().get("database")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO Card_in_Storage (card_code, storage_id, count, page) VALUES (?, ?, ?, ?)
    ''', (
        card_code,
        storage_id,
        count,
        page, 
    ))
    conn.commit()

    print("\nCard saved successfully!\n")