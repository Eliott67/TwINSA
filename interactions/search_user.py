#Search Users

from ..users_db import UsersDatabase
from ..user import User

def go_to_search_bar():
    print("\n--- Search Users ---")
    history = []

    # Fonction to search users

    def search(query):
        nonlocal history # Access the outer scope variable
        history.insert(0, query) #add to the start of the list
        history = history[:5]  # Keep only the last 5 searches
        print(f"Searching for users matching: '{query}'")
        print("Search History:", history)


    # Fonction to clear search history

    def clear_history():
        nonlocal history
        history.clear()
        print("Search history cleared.")
        print("Search History:", history)

    
    # Simulation
    print("User is searching for users")
    search("Alice")
    search("Bob")
    search("Charlie")
    search("David")
    search("Eve")
    search("Frank")  # This will push out "Alice" from history
    print("\nUser decides to clear search history")
    clear_history()

if __name__ == "__main__":
    go_to_search_bar()


