def new_card():
    import questionary
    from .db_access import card_to_storage, rarity_fetch
    from .api_fetch import fetch_set

    print("NEW CARD\n")
    card_code = input("Enter card set code: ").upper()
    fetch_set(card_code)

    rarity = rarity_fetch(card_code)

    card_rarity = questionary.select("Select rarity of the card you want to add to storage", rarity).ask()

    print("\nSTORAGE INFO")
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


def create_database():
    from .db_access import create_db

    create_db()


def test_database_conn():
    from .db_access import db_connect

    if db_connect():
        print("Connection succeed")
    
    else:
        print("Connection failed")