def main():
    import sqlite3
    import questionary

    DB_FILE = "YGO.db"

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


if __name__ == "__main__":
    main()
