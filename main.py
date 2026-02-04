import questionary
from scripts.functions import *

choices={
    "Add new card": new_card,
    "Add new storage": new_storage,
    "Transfer cards": transfer_cards,
    "Create new database": create_database,
    "Test database connection": test_database_conn,
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