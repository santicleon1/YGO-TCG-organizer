def main():

    import requests
    import sqlite3
    import os
    import time

    # constants
    DB_FILE = "YGO.db"
    IMAGE_FOLDER = "images/card/"
    CARD_API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php?id={}"

    # connection
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    read_cur = conn.cursor()

    # image downloader
    def download_image(url, card_id, folder=IMAGE_FOLDER):
        if not url:
            return None
        os.makedirs(folder, exist_ok=True)
        local_file = os.path.join(folder, f"{card_id}.jpg")
        if not os.path.exists(local_file):
            r = requests.get(url)
            with open(local_file, 'wb') as f:
                f.write(r.content)
        return local_file

    # main fetcher
    def fetch_card():
        # Fetch card data
        response = requests.get(CARD_API_URL.format(card_id))
        if response.status_code != 200:
            print(f"Error fetching card {card_id}: {response.status_code}")
            exit()

        card_data = response.json().get("data")[0]
        # Insert card into Card table
        cursor.execute('''
        INSERT OR REPLACE INTO Card 
        (id, name, type, race, level, atk, def, attribute, archetype, desc, linkval, linkmarkers, scale)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        card_data.get("scale")
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

        # result confirmation
        conn.commit()
        print(f"{row_counter} / {row_top} -- {card_data.get('name')} (ID {card_id}) restored successfully.")


    read_cur.execute("SELECT COUNT(*) FROM Card")
    row_top = read_cur.fetchone()[0]
    row_counter = 0
    read_cur.execute("SELECT id FROM Card")

    while row_counter < row_top:
        card_id = read_cur.fetchone()[0]
        row_counter += 1

        fetch_card()
        time.sleep(0.1) # to not clog API

    print("Successfully")
    return

    

if __name__ == "__main__":
	main()