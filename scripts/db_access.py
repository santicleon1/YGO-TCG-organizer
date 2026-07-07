def db_connect():
    import psycopg
    from .utils import read_config

    try:
        return psycopg.connect(
        dbname = read_config().get("database_connection").get("database"),
        user = read_config().get("database_connection").get("user"),
        password = read_config().get("database_connection").get("password"),
        host = read_config().get("database_connection").get("host"),
        port = read_config().get("database_connection").get("port")
    )
        
    except:
        return None
    

def create_db():
    import questionary

    conn = db_connect()
    cursor = conn.cursor()

	# Cards table
    cursor.execute('''
	CREATE TABLE card (
        id int4 NOT NULL,
        "name" text NOT NULL,
        "type" text NULL,
        race text NULL,
        "level" int4 NULL,
        atk int4 NULL,
        def int4 NULL,
        linkval int4 NULL,
        linkmarkers text NULL,
        "scale" int4 NULL,
        "attribute" text NULL,
        archetype text NULL,
        description text NULL,
        banlist text NULL,
                
        CONSTRAINT card_pkey PRIMARY KEY (id)
);
	''')

	# CardSets table
    cursor.execute('''
	CREATE TABLE card_set (
        card_id int4 NOT NULL,
        set_code text NOT NULL,
        set_name text NOT NULL,
        set_rarity text NOT NULL,
 
        CONSTRAINT card_set_pkey PRIMARY KEY (set_code, set_rarity),
        CONSTRAINT card_set_card_id_fkey FOREIGN KEY (card_id) REFERENCES public.card(id)
    );
	''')

	# CardImages table
    cursor.execute('''
	CREATE TABLE public.card_image (
        card_id int4 NOT NULL,
        image bytea NOT NULL,
                
        CONSTRAINT card_image_pkey PRIMARY KEY (card_id),
        CONSTRAINT card_image_card_id_fkey FOREIGN KEY (card_id) REFERENCES public.card(id)
    );
	''')

	# Storage table
    cursor.execute('''
	CREATE TABLE public."storage" (
        id int4 NOT NULL,
        color text NOT NULL,
        "type" text NOT NULL,
                
        CONSTRAINT storage_pkey PRIMARY KEY (id)
    );
	''')

	# Card in Storage table
    cursor.execute('''
	CREATE TABLE public.card_in_storage (
        card_code text NOT NULL,
        card_rarity text NOT NULL,
        storage_id int4 NOT NULL,
        page int4 NOT NULL,
        count int4 NOT NULL,
        CONSTRAINT card_in_storage_pkey PRIMARY KEY (card_code, storage_id, page),
        CONSTRAINT card_in_storage_card_code_card_rarity_fkey FOREIGN KEY (card_code,card_rarity) REFERENCES public.card_set(set_code,set_rarity),
        CONSTRAINT card_in_storage_storage_id_fkey FOREIGN KEY (storage_id) REFERENCES public."storage"(id)
    );
	''')
    conn.commit()

    questionary.print("Database created successfully.", style="bold fg:green")
    return


def create_storage():
    import questionary
    conn = db_connect()
    cursor = conn.cursor()

    ID = int(input("Enter Storage ID: "))
    
    cursor.execute("SELECT id FROM storage WHERE id = %s", (ID,))
    if cursor.fetchone():
        questionary.print("Storage already exists!", style="bold fg:red")
        return
        

    color = input("Enter Storage color: ")
    stor_type = input("Enter type of Storage: ")

    cursor.execute('''
    INSERT INTO storage (id, color, type) VALUES (%s, %s, %s)
    ''', (
        ID,
        color,
        stor_type,
    ))

    conn.commit()

    questionary.print(f"\nNew Storage entry with id {ID} created successfully.", style="bold fg:green")
    return


def transfer_card_in_storage():
    import questionary

    conn = db_connect()
    cur = conn.cursor()

    try:
        card_code = input("Card set: ").upper()

        cur.execute(
            """
            SELECT DISTINCT storage_id
            FROM card_in_storage
            WHERE card_code = %s
            """,
            (card_code,)
        )
        storages = [str(r[0]) for r in cur.fetchall()]
        if not storages:
            questionary.print("No cards found for that card_code", style="bold fg:yellow")
            return

        from_storage = questionary.select(
            "Select source storage:",
            choices=storages
        ).ask()

        cur.execute(
            """
            SELECT page
            FROM card_in_storage
            WHERE card_code = %s AND storage_id = %s
            """,
            (card_code, from_storage)
        )
        pages = [str(r[0]) for r in cur.fetchall()]
        if not pages:
            questionary.print("No pages found in selected storage", style="bold fg:yellow")
            return

        from_page = questionary.select(
            "Select source page:",
            choices=pages
        ).ask()

        move_amount = int(questionary.text("Amount to transfer:").ask())
        to_storage = questionary.text("Destination storage:").ask()
        to_page = questionary.text("Destination page:").ask()

        cur.execute(
            """
            SELECT "count", card_rarity
            FROM card_in_storage
            WHERE card_code = %s AND storage_id = %s AND page = %s
            """,
            (card_code, from_storage, from_page)
        )
        row = cur.fetchone()
        if not row:
            questionary.print("Source location not found", style="bold fg:yellow")
            return

        current_count, card_rarity = row
        if move_amount > current_count or move_amount <= 0:
            questionary.print(f"Invalid amount. Current count: {current_count}", style="bold fg:red")
            return

        cur.execute(
            """
            UPDATE card_in_storage
            SET "count" = "count" - %s
            WHERE card_code = %s AND storage_id = %s AND page = %s
            """,
            (move_amount, card_code, from_storage, from_page)
        )

        cur.execute(
            """
            DELETE FROM card_in_storage
            WHERE card_code = %s
              AND storage_id = %s
              AND page = %s
              AND "count" = 0
            """,
            (card_code, from_storage, from_page)
        )

        cur.execute(
            """
            INSERT INTO card_in_storage (card_code, card_rarity, storage_id, page, "count")
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (card_code, storage_id, page)
            DO UPDATE
            SET "count" = card_in_storage."count" + EXCLUDED."count"
            """,
            (card_code, card_rarity, to_storage, to_page, move_amount)
        )

        conn.commit()

        questionary.print(
            f"Transferred {move_amount} card(s) of rarity '{card_rarity}' "
            f"from {from_storage}/{from_page} to {to_storage}/{to_page}",
            style="bold fg:green"
        )

    except:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


def card_to_storage(card_code, card_rarity, storage_id, count, page):
    import questionary
    conn = db_connect()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO card_in_storage (card_code, card_rarity, storage_id, count, page) VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (card_code, storage_id, page)
    DO UPDATE
    SET
        card_code = EXCLUDED.card_code,
        card_rarity = EXCLUDED.card_rarity,
        storage_id = EXCLUDED.storage_id,
        count = EXCLUDED.count,
        page = EXCLUDED.page
                   ''', (
        card_code,
        card_rarity,
        storage_id,
        count,
        page, 
    ))
    conn.commit()

    questionary.print("\nCard saved successfully!\n", style="bold fg:green")


def rarity_fetch(set_code):
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT set_rarity FROM card_set WHERE set_code = %s;
                   ''', (set_code,))
    
    return [item[0] for item in cursor.fetchall()]


def transfer_page(set_page, storage_id, from_page):
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE card_in_storage SET page = %s WHERE storage_id = %s AND page = %s;
                   ''', (set_page, storage_id, from_page,))
    
    conn.commit()