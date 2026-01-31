def main():
	import sqlite3

	conn = sqlite3.connect("YGO.db")
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


if __name__ == "__main__":
	main()