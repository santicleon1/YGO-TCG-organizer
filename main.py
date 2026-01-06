import questionary
from scripts import new_card, new_storage, create_db

choices={
    "Add new card": new_card.main,
    "Add new storage": new_storage.main,
    "Create new database": create_db.main,
    "Exit": None
}

def main():
    while True:
        print('''
+-----------------------------+
|Yu-Gi-Oh! collection database|
+-----------------------------+
''')

        selection = questionary.select("Main menu", choices).ask()
        
        if selection != "Exit":
            choices[selection]()
        else:
            return
    

if __name__ == "__main__":
	main()