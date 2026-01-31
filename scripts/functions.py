def new_card():
    import questionary
    from .db_access import card_to_storage
    from .api_fetch import fetch_set

    print("NEW CARD\n")
    card_code = input("Enter card set code: ").upper()
    fetch_set(card_code)

    print("\nSTORAGE INFO")
    storage_id = int(input("Enter ID of storage location of this card: "))
    storage_page = int(input("Enter page number card is located on: "))
    card_count = int(input("Enter count: "))
    card_to_storage(card_code, storage_id, card_count, storage_page)

    selection = questionary.select("Add another card?", choices).ask()
    
    choices = {
        "Yes": new_card,
        "No": None
    }

    if selection != "No":
        choices[selection]()
    else:
        return

    new_card()


def new_storage():
    from .db_access import create_storage
    
    create_storage()


def transfer_cards():
    from .db_access import transfer_card_in_storage

    transfer_card_in_storage()

def create_database():
    from .db_access import create_db

    create_db()