def new_card():
    import questionary
    from .utils import read_config
    from .db_access import card_to_storage, rarity_fetch
    from .api_fetch import fetch_set

    print("NEW CARD\n")
    card_code = input("Enter card set code: ").upper()
    fetch_set(card_code)

    rarity = rarity_fetch(card_code)

    card_rarity = questionary.select("Select rarity of the card you want to add to storage", rarity).ask()

    print("\nSTORAGE INFO")

    if not read_config().get("default_storage"):
        questionary.print("\nNo default storage set! Please enter storage info for this card.", style="bold fg:yellow")
        storage_id = int(input("Enter ID of storage location of this card: "))
        storage_page = int(input("Enter page number card is located on: "))

    else:
        if questionary.confirm("\nDefault storage found! Do you want to use it for this card?").ask():
            storage_id = read_config().get("default_storage").get("storage_id")
            storage_page = read_config().get("default_storage").get("page")
        else:
            storage_id = int(input("Enter ID of storage location of this card: "))
            storage_page = int(input("Enter page number card is located on: "))
    
    card_count = int(input("Enter count: "))
    card_to_storage(card_code, card_rarity, storage_id, card_count, storage_page)

    choices = {
        "Yes": new_card,
        "No": None
    }

    selection = questionary.select("Add another card?", choices).ask()
    

    if selection != "No":
        choices[selection]()
    else:
        return


def new_storage():
    from .db_access import create_storage
    
    create_storage()


def transfer_cards():
    from .db_access import transfer_card_in_storage

    transfer_card_in_storage()


def transfer_page():
    import questionary
    from .db_access import transfer_page

    storage_id = int(questionary.text("Enter storage id:").ask())
    from_page = int(questionary.text("ID of page you want to transfer:").ask())
    set_page = int(questionary.text("ID of page you want to transfer to:").ask())
    
    transfer_page(set_page, storage_id, from_page)


def create_database():
    # creates whole DB structure in configured DB
    from .db_access import create_db

    create_db()


def test_database_conn():
    # makes connection to a DB and returns result
    from .db_access import db_connect
    import questionary

    if db_connect():
        questionary.print(f"Connection succeed", style="bold fg:green")
    
    else:
        questionary.print(f"Connection failed", style="bold fg:red")


def current_storage():
    import questionary
    from .db_access import db_connect
    from .utils import write_config, read_config

    conn = db_connect()
    cur = conn.cursor()

    storage_id = int(input("Enter Storage ID: "))
    
    cur.execute('''SELECT id FROM storage WHERE id = %s''', (storage_id,))
    if cur.fetchone():
        page = int(input("Page number: "))
        data = {"storage_id": storage_id, "page": page}

        config_data = read_config()
        config_data["default_storage"] = data
        
        write_config(config_data)
        questionary.print("\nConfig written successfully!", style="bold fg:green")

        return

    else:
        questionary.print("\nStorage ID not found in database!", style="bold fg:red")
        return  

    


    