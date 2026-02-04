def download_image(url):
    import requests

    if not url:
        return None
    
    image = requests.get(url)
    if image.status_code == 200:
        return image.content
    return None


def fetch_card(card_id):
    import requests
    from .utils import config
    from .db_access import db_connect

    CARD_API_URL = config().get("api_url_id")

    # Fetch card data
    response = requests.get(CARD_API_URL.format(card_id))
    if response.status_code != 200:
        print(f"Error fetching card {card_id}: {response.status_code}")
        exit()

    card_data = response.json().get("data")[0]
    ban_data = card_data.get("banlist_info")

    # Insert card into Card table
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO card 
    (id, name, type, race, level, atk, def, attribute, archetype, description, linkval, linkmarkers, scale, banlist)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id)
    DO UPDATE
    SET
        name = EXCLUDED.name,
        type = EXCLUDED.type,
        race = EXCLUDED.race,
        level = EXCLUDED.level,
        atk = EXCLUDED.atk,
        def = EXCLUDED.def,
        attribute = EXCLUDED.attribute,
        archetype = EXCLUDED.archetype,
        description = EXCLUDED.description,
        linkval = EXCLUDED.linkval,
        linkmarkers = EXCLUDED.linkmarkers,
        scale = EXCLUDED.scale,
        banlist = EXCLUDED.banlist
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
    ban_data.get("ban_tcg") if ban_data else None,
    ))

    conn.commit()

    # Insert images
    for img in card_data.get("card_images", []):
        image = download_image(img.get("image_url"))
        cursor.execute('''
            INSERT INTO card_image (card_id, image)
            VALUES (%s, %s)
            ON CONFLICT (card_id)
            DO UPDATE
            SET
                card_id = EXCLUDED.card_id,
                image = EXCLUDED.image
            ''', (
            card_data.get("id"),
            image,
        ))
    
    conn.commit()

    return card_data


def fetch_set(card_code):
    import requests
    from .utils import config
    from .db_access import db_connect

    SET_API_URL = config().get("api_url_set")

    conn = db_connect()
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
        INSERT INTO card_set (card_id, set_name, set_code, set_rarity)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (set_code, set_rarity)
        DO UPDATE
        SET
            card_id = EXCLUDED.card_id,
            set_name = EXCLUDED.set_name,
            set_code = EXCLUDED.set_code,
            set_rarity = EXCLUDED.set_rarity
        ''', (
        set_data.get("id"),
        set_data.get("set_name"),
        set_data.get("set_code"),
        check_rarity(card_sets, card_code),
    ))

    conn.commit()


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