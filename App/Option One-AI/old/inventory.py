import datetime
from typing import List, Optional
import json  # Required for saving and loading data
import os  # Required for file cleanup in the demo


class InventoryItem:
    """
    Represents a single item in the inventory.
    """

    # Updated __init__ to accept an optional date_added for loading purposes
    def __init__(self, name: str, quantity: int, price: float, date_added: Optional[datetime.datetime] = None):
        if not name or quantity < 0 or price < 0:
            raise ValueError("Name cannot be empty, quantity and price must be non-negative.")

        self.name: str = name
        self.quantity: int = quantity
        self.price: float = price
        # Use provided date if loading, otherwise use current time
        self.date_added: datetime.datetime = date_added if date_added is not None else datetime.datetime.now()

    def __repr__(self):
        """String representation for debugging and display."""
        return (f"InventoryItem(Name='{self.name}', Quantity={self.quantity}, "
                f"Price=${self.price:.2f}, Added='{self.date_added.strftime('%Y-%m-%d %H:%M:%S')}')")

    def to_dict(self):
        """
        Returns a dictionary representation of the item, converting the datetime
        object to an ISO-formatted string for JSON serialization.
        """
        return {
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price,
            'date_added': self.date_added.isoformat()  # Convert datetime to string
        }


class InventoryManager:
    """
    Manages a collection of InventoryItem objects, providing functionality
    for adding, editing, sorting, saving, and loading items.
    """

    def __init__(self):
        self.items: List[InventoryItem] = []

    def add_item(self, item: InventoryItem):
        """Adds a new item to the inventory."""
        if any(i.name.lower() == item.name.lower() for i in self.items):
            print(f"Error: Item '{item.name}' already exists.")
            return

        self.items.append(item)
        print(f"Successfully added: {item.name}")

    # --- Persistence Methods ---

    def save_inventory(self, filename: str = "inventory_data.json"):
        """Saves the current inventory to a JSON file."""
        # Convert all InventoryItem objects to a list of serializable dictionaries
        data_to_save = [item.to_dict() for item in self.items]
        try:
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=4)  # Use indent for readability
            print(f"\n[SYSTEM] Successfully saved inventory data ({len(self.items)} items) to '{filename}'.")
        except IOError as e:
            print(f"\n[SYSTEM ERROR] Error saving inventory: {e}")

    def load_inventory(self, filename: str = "inventory_data.json"):
        """Loads inventory data from a JSON file, replacing the current inventory."""
        try:
            with open(filename, 'r') as f:
                data_loaded = json.load(f)

            self.items.clear()  # Clear existing inventory

            for item_data in data_loaded:
                # Convert the ISO string back to a datetime object
                date_obj = datetime.datetime.fromisoformat(item_data['date_added'])

                # Re-create the InventoryItem using the loaded data, including the original date
                new_item = InventoryItem(
                    name=item_data['name'],
                    quantity=item_data['quantity'],
                    price=item_data['price'],
                    date_added=date_obj
                )
                self.items.append(new_item)

            print(f"\n[SYSTEM] Successfully loaded {len(self.items)} items from '{filename}'.")

        except FileNotFoundError:
            print(f"\n[SYSTEM] No save file found at '{filename}'. Starting with an empty inventory.")
        except json.JSONDecodeError:
            print(f"\n[SYSTEM ERROR] Could not decode JSON data from '{filename}'. File corrupted.")
        except Exception as e:
            # Catch other potential errors like missing keys
            print(f"\n[SYSTEM ERROR] An error occurred during loading: {e}")

    # --- Other Methods ---
    def get_item_by_name(self, name: str) -> Optional[InventoryItem]:
        """Retrieves an item by its name (case-insensitive)."""
        for item in self.items:
            if item.name.lower() == name.lower():
                return item
        return None
                    # PYTHON REMOVE RUNS O(N), CAN BE REPLACE WITH BINARY SEARCH
    def remove_item(self, name: str):
        """Removes an item from the inventory by name."""
        item_to_remove = self.get_item_by_name(name)
        if item_to_remove:
            self.items.remove(item_to_remove)
            print(f"[SUCCESS] Successfully removed: {name}")
        else:
            print(f"[ERROR] Item '{name}' not found.")

    def edit_item(self, name: str, new_quantity: Optional[int] = None, new_price: Optional[float] = None):
        """Edits the quantity or price of an existing item."""
        item = self.get_item_by_name(name)
        if not item:
            print(f"[ERROR] Cannot edit. Item '{name}' not found.")
            return

        updated_fields = []
        if new_quantity is not None and new_quantity >= 0:
            item.quantity = new_quantity
            updated_fields.append(f"Quantity -> {new_quantity}")
        elif new_quantity is not None and new_quantity < 0:
            print("[WARNING] Quantity must be non-negative. Quantity not changed.")

        if new_price is not None and new_price >= 0:
            item.price = new_price
            updated_fields.append(f"Price -> ${new_price:.2f}")
        elif new_price is not None and new_price < 0:
            print("[WARNING] Price must be non-negative. Price not changed.")

        if updated_fields:
            print(f"[SUCCESS] Successfully updated '{name}'. Changes: {', '.join(updated_fields)}")
        else:
            print(f"No valid updates provided for '{name}'.")



    def sort_inventory(self, key: str):
        """
        Sorts the inventory based on the specified key.
        Valid keys: 'name', 'date', 'quantity', 'price'.
        """
        key = key.lower()

        sort_key_map = {
            'name': (lambda item: item.name.lower(), "Name (Alphabetical)"),
            'alphabetical': (lambda item: item.name.lower(), "Name (Alphabetical)"),
            'date': (lambda item: item.date_added, "Date Added (Oldest first)"),
            'quantity': (lambda item: item.quantity, "Quantity (Low to High)"),
            'price': (lambda item: item.price, "Price (Low to High)")
        }

        if key in sort_key_map:
            sort_func, label = sort_key_map[key]
            self.items.sort(key=sort_func)
            print(f"\n[SUCCESS] Inventory sorted by {label}")
        else:
            print(f"[ERROR] Invalid sorting key '{key}'. Valid keys are: name, date, quantity, price.")

    def display_inventory(self):
        """Prints the current inventory items in a formatted table."""
        if not self.items:
            print("\n--- Inventory is Empty ---")
            return

        print("\n" + "=" * 80)
        print(f"{'Name':<25} {'Quantity':<10} {'Price':<10} {'Date Added':<30}")
        print("-" * 80)
        for item in self.items:
            date_str = item.date_added.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{item.name:<25} {item.quantity:<10} ${item.price:<9.2f} {date_str:<30}")
        print("=" * 80 + "\n")


def main_menu():
    """Displays the main menu options."""
    print("\n" + "#" * 40)
    print("## INVENTORY MANAGEMENT SYSTEM ##")
    print("#" * 40)
    print("1. Add New Item")
    print("2. Edit Existing Item")
    print("3. Remove Item")
    print("4. Sort Inventory")
    print("5. Display Inventory")
    print("6. Save & Exit")
    print("-" * 40)
    return input("Enter your choice (1-6): ")


def get_valid_input(prompt: str, data_type: type, non_negative: bool = False, optional: bool = False) -> Optional[any]:
    """Helper function to safely get and validate user input."""
    while True:
        user_input = input(prompt).strip()
        if optional and not user_input:
            return None
        if not user_input:
            print("[INPUT ERROR] Input cannot be empty.")
            continue

        try:
            value = data_type(user_input)
            if non_negative and value < 0:
                print(f"[INPUT ERROR] Value must be non-negative (0 or greater).")
                continue
            return value
        except ValueError:
            print(f"[INPUT ERROR] Invalid input. Expected a {data_type.__name__}.")


def run_app():
    """Main application loop."""
    manager = InventoryManager()
    manager.load_inventory()  # Load inventory on startup

    while True:
        choice = main_menu()

        if choice == '1':
            # Add New Item
            print("\n--- ADD NEW ITEM ---")
            name = input("Enter item name: ").strip()
            if manager.get_item_by_name(name):
                print(f"[ERROR] Item '{name}' already exists.")
                continue
            quantity = get_valid_input("Enter quantity (integer): ", int, non_negative=True)
            price = get_valid_input("Enter price (float): $", float, non_negative=True)

            if name and quantity is not None and price is not None:
                try:
                    new_item = InventoryItem(name, quantity, price)
                    manager.add_item(new_item)
                except ValueError as e:
                    print(f"[ERROR] Failed to create item: {e}")

        elif choice == '2':
            # Edit Existing Item
            print("\n--- EDIT ITEM ---")
            name_to_edit = input("Enter name of item to edit: ").strip()
            # POSSIBLE IMPROVEMENT: searching with if takes O(N), can instead search for item using binary search
            if not manager.get_item_by_name(name_to_edit):
                print(f"[ERROR] Item '{name_to_edit}' not found.")
                continue

            print("Enter new quantity and price. Press ENTER to skip a field.")
            new_quantity = get_valid_input("New quantity (integer, optional): ", int, non_negative=True, optional=True)
            new_price = get_valid_input("New price (float, optional): $", float, non_negative=True, optional=True)

            manager.edit_item(name_to_edit, new_quantity, new_price)

        elif choice == '3':
            # Remove Item
            print("\n--- REMOVE ITEM ---")
            name_to_remove = input("Enter name of item to remove: ").strip()
            manager.remove_item(name_to_remove)

        elif choice == '4':
            # Sort Inventory
            print("\n--- SORT INVENTORY ---")
            sort_key = input("Sort by (name, date, quantity, price): ").strip()
            manager.sort_inventory(sort_key)

        elif choice == '5':
            # Display Inventory
            manager.display_inventory()

        elif choice == '6':
            # Save and Exit
            print("\n--- EXITING APPLICATION ---")
            manager.save_inventory()
            break

        else:
            print("\n[INPUT ERROR] Invalid choice. Please select a number between 1 and 6.")


# --- Main Entry Point ---
if __name__ == "__main__":
    # Remove the file cleanup, as we want the file to persist between runs
    # if os.path.exists("inventory_data.json"):
    #     os.remove("inventory_data.json")
    run_app()