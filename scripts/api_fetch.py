def download_image(url, card_id):
    import os
    import requests
    from .utils import config

    folder = config().get("image_folder")

    if not url:
        return None
    os.makedirs(folder, exist_ok=True)
    local_file = os.path.join(folder, f"{card_id}.jpg")
    if not os.path.exists(local_file):
        r = requests.get(url)
        with open(local_file, 'wb') as f:
            f.write(r.content)
    return local_file


def fetch_card(card_id):
    import sqlite3
    import requests
    from .utils import config

    CARD_API_URL = config().get("api_url_id")
    DB_FILE = config().get("database")

    # Fetch card data
    response = requests.get(CARD_API_URL.format(card_id))
    if response.status_code != 200:
        print(f"Error fetching card {card_id}: {response.status_code}")
        exit()

    card_data = response.json().get("data")[0]
    ban_data = card_data.get("banlist_info")
    ban_tcg = ban_data.get("ban_tcg") if ban_data else None

    # Insert card into Card table
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO Card 
    (id, name, type, race, level, atk, def, attribute, archetype, desc, linkval, linkmarkers, scale, banlist)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
    card_id,
    card_data.get("name"),
    card_data.get("type"),
    card_data.get("race"),
    card_data.get("level"),
    card_data.get("atk"),
    card_data.get("def"),
    card_data.get("attribute"),
    card_data.get("archetype"),
    card_data.get("desc"),
    card_data.get("linkval"),
    ",".join(card_data.get("linkmarkers", [])) if card_data.get("linkmarkers") else None,
    card_data.get("scale"),
    ban_tcg
    ))

    # Insert images
    for img in card_data.get("card_images", []):
        local_path = download_image(img.get("image_url"), card_data.get("id"))
        cursor.execute('''
            INSERT OR REPLACE INTO Card_Image (card_id, image)
            VALUES (?, ?)
            ''', (
            card_data.get("id"),
            local_path,
        ))


def fetch_set(card_code):
    import sqlite3
    import requests
    from .utils import config

    DB_FILE = config().get("database")
    SET_API_URL = config().get("api_url_set")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Fetch card set data
    response = requests.get(SET_API_URL.format(card_code))
    if response.status_code != 200:
        print(f"Error fetching card set {card_code}: {response.status_code}")
        exit()

    set_data = response.json()

    card_sets = fetch_card(set_data.get("id"))["card_sets"]

    # Insert sets
    cursor.execute('''
        INSERT OR REPLACE INTO Card_Set (card_id, set_name, set_code, set_rarity)
        VALUES (?, ?, ?, ?)
        ''', (
        set_data.get("id"),
        set_data.get("set_name"),
        set_data.get("set_code"),
        check_rarity(card_sets, card_code),
    ))


def check_rarity(card_sets, target_set_code):
    import questionary

    matching_sets = []
    for cs in card_sets:
        if cs["set_code"] == target_set_code:
            matching_sets.append(cs["set_rarity"])

    if not matching_sets:
        print(f"No entries found for set code {target_set_code}")
        return None

    if len(matching_sets) == 1:
        return matching_sets[0]

    choices = []
    for cs in matching_sets:
        choices.append(cs)

    selected_label = questionary.select(
        "Multiple rarities found for this set. Choose one:",
        choices=choices
    ).ask()

    for cs in matching_sets:
        if cs == selected_label:
            return cs

    return None