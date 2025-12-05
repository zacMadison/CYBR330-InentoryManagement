import datetime
from typing import List, Optional, Dict, Any
from linked_queue import LinkedQueue
import json
import os


# --- New Category Tree Structure ---

class CategoryNode:
    """Represents a single node in the category hierarchy."""

    # Changed by Zach M. added variable to track inventory items
    def __init__(self, name: str):
        self.name: str = name
        self.children: List['CategoryNode'] = []
        self.items = []

    def to_dict(self) -> Dict[str, Any]:
        """Converts the node and its children to a serializable dictionary."""
        return {
            'name': self.name,
            'children': [child.to_dict() for child in self.children]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CategoryNode':
        """Recreates a CategoryNode instance from a dictionary."""
        node = CategoryNode(data['name'])
        for child_data in data.get('children', []):
            node.children.append(CategoryNode.from_dict(child_data))
        return node


# --- Inventory Item Class ---

class InventoryItem:
    """
    Represents a single item in the inventory, now including a category path.
    """

    def __init__(self, name: str, quantity: int, price: float, category_path: List[str],
                 date_added: Optional[datetime.datetime] = None):
        if not name or quantity < 0 or price < 0:
            raise ValueError("Name cannot be empty, quantity and price must be non-negative.")

        self.name: str = name
        self.quantity: int = quantity
        self.price: float = price
        self.category_path: List[str] = category_path
        self.date_added: datetime.datetime = date_added if date_added is not None else datetime.datetime.now()

    def __repr__(self):
        """String representation for debugging and display."""
        category_str = ' > '.join(self.category_path)
        return (f"InventoryItem(Name='{self.name}', Quantity={self.quantity}, "
                f"Price=${self.price:.2f}, Category='{category_str}')")

    def to_dict(self):
        """Returns a dictionary representation for JSON serialization."""
        return {
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price,
            'date_added': self.date_added.isoformat(),
            'category_path': self.category_path
        }


# --- Inventory Manager Class ---

class InventoryManager:
    """
    Manages a collection of InventoryItem objects and the Category hierarchy.
    """

    def __init__(self):
        self.items: List[InventoryItem] = []
        # Initialize the root of the category tree (used as a hidden container for top-level categories)
        self.category_tree: CategoryNode = CategoryNode("ROOT")

        # --- Category Management Methods ---

    def find_category_node(self, path: List[str]) -> Optional[CategoryNode]:
        """Traverses the tree to find a specific node based on its path."""
        current_node = self.category_tree

        # If path is empty, return the root node (useful for starting iteration)
        if not path:
            return current_node

        for segment in path:
            found = False
            for child in current_node.children:
                if child.name.lower() == segment.lower():
                    current_node = child
                    found = True
                    break
            if not found:
                return None  # Category path not found
        return current_node

    def add_category(self, path: List[str]):
        """Adds a new category based on the provided path (e.g., ['Electronics', 'Laptops'])."""
        if not path:
            print("[ERROR] Category path cannot be empty.")
            return

        parent_path = path[:-1]
        new_category_name = path[-1]

        # 1. Check if the parent path exists
        parent_node = self.find_category_node(parent_path)
        if not parent_node:
            print(
                f"[ERROR] Parent path '{' > '.join(parent_path)}' does not exist. Please create parent categories first.")
            return

        # 2. Check if the category already exists under the parent
        if any(c.name.lower() == new_category_name.lower() for c in parent_node.children):
            print(f"[ERROR] Category '{new_category_name}' already exists under this path.")
            return

        # 3. Add the new category
        parent_node.children.append(CategoryNode(new_category_name))
        print(f"[SUCCESS] Added category: {' > '.join(path)}")

    def display_category_tree(self, node: Optional[CategoryNode] = None, level: int = 0):
        """Iteratively prints the category tree structure without recursion,
        perfectly matching the recursive version's behavior."""

        # Match recursive behavior: If node is None, use ROOT and print header
        if node is None:
            node = self.category_tree
            print("\n--- Current Category Tree ---")

        # Explicit stack for iterative DFS
        # (node, level, visited_children_flag)
        stack = [(node, level, False)]

        while stack:
            node, level, visited = stack.pop()

            if not visited:
                # Simulate recursive behavior:
                # First time we see the node:
                #   1) print (if not ROOT)
                #   2) then schedule children
                #   3) then schedule node again as "visited"

                # Print same as recursive version
                if node.name != "ROOT":
                    prefix = "  " * (level - 1)
                    print(f"{prefix}└── {node.name}")

                # Push back this node to handle after children
                stack.append((node, level, True))

                # Push children in reverse order for correct print order
                for child in reversed(node.children):
                    stack.append((child, level + 1, False))

            else:
                # After all children processed
                if level == 0:
                    # Match recursive version ending line
                    print("-----------------------------\n")

    # --- Item Management Methods ---


    # changed by Zach M. now category tree actually stores items
    def add_item(self, item: InventoryItem):
        """Adds a new item to the inventory, ensuring the category exists."""
        if any(i.name.lower() == item.name.lower() for i in self.items):
            print(f"[ERROR] Item '{item.name}' already exists.")
            return

        # Validate category path before adding item
        if item.category_path and not self.find_category_node(item.category_path):
            print(f"[ERROR] Category path {' > '.join(item.category_path)} does not exist. Please create it first.")
            return

        self.items.append(item)
        if item.category_path:
            node = self.find_category_node(item.category_path)
            node.items.append(item)
        print(f"[SUCCESS] Successfully added: {item.name}")

    def edit_item(self, name: str, new_quantity: Optional[int] = None, new_price: Optional[float] = None,
                  new_category_path: Optional[List[str]] = None):
        """Edits the quantity, price, or category of an existing item."""
        item = self.get_item_by_name(name)
        if not item:
            print(f"[ERROR] Cannot edit. Item '{name}' not found.")
            return

        updated_fields = []

        # Update Quantity
        if new_quantity is not None and new_quantity >= 0:
            item.quantity = new_quantity
            updated_fields.append(f"Quantity -> {new_quantity}")
        elif new_quantity is not None and new_quantity < 0:
            print("[WARNING] Quantity must be non-negative. Quantity not changed.")

        # Update Price
        if new_price is not None and new_price >= 0:
            item.price = new_price
            updated_fields.append(f"Price -> ${new_price:.2f}")
        elif new_price is not None and new_price < 0:
            print("[WARNING] Price must be non-negative. Price not changed.")

        # Update Category Path
        # CHANGED BY ZACH M: Now also changes items inside tree when category path is updated
        # Bug fix: would previously trigger, even if not changed because new_category_path input is never none
            # bug may be present elsewhere
        if not new_category_path == []:
            if new_category_path and not self.find_category_node(new_category_path):
                print(
                    f"[ERROR] New category path {' > '.join(new_category_path)} does not exist. Category not changed.")
            else:
                if not item.category_path == []:
                    node = self.find_category_node(item.category_path)
                    node.items.remove(item)
                item.category_path = new_category_path
                new_node = self.find_category_node(item.category_path)
                new_node.items.append(item)
                updated_fields.append(f"Category -> {' > '.join(new_category_path)}")

        if updated_fields:
            print(f"[SUCCESS] Successfully updated '{name}'. Changes: {', '.join(updated_fields)}")
        else:
            print(f"No valid updates provided for '{name}'.")

    def get_item_by_name(self, name: str) -> Optional[InventoryItem]:
        """Retrieves an item by its name (case-insensitive)."""
        # POSSIBLE IMPROVEMENT: Can be done with Binary Search (Issue #5)
        for item in self.items:
            if item.name.lower() == name.lower():
                return item
        return None

    # POSSIBLE IMPROVEMENT .remove takes O(N), can be done faster if list is sorted (Issue #5)
    def remove_item(self, name: str):
        """Removes an item from the inventory by name."""
        item_to_remove = self.get_item_by_name(name)
        if item_to_remove:
            self.items.remove(item_to_remove)
            print(f"[SUCCESS] Successfully removed: {name}")
        else:
            print(f"[ERROR] Item '{name}' not found.")

    # POSSIBLE IMPROVEMENT  (issue #4)
    # Program uses .sort, python implementation of sort uses Timsort, this runs in the same time.
    # The drawback of Timsort is that it uses O(n) Auxiliary space,
    # where heap sort only takes O(n) total space (O(1) Auxiliary space)
    def sort_inventory(self, key: str):
        """
        Sorts the inventory based on the specified key.
        Valid keys: 'name', 'date', 'quantity', 'price', 'category'.
        """
        key = key.lower()

        sort_key_map = {
            'name': (lambda item: item.name.lower(), "Name (Alphabetical)"),
            'date': (lambda item: item.date_added, "Date Added (Oldest First)"),
            'quantity': (lambda item: item.quantity, "Quantity (Low to High)"),
            'price': (lambda item: item.price, "Price (Low to High)"),
            'category': (lambda item: ' > '.join(item.category_path).lower(), "Category Path")
        }

        if key not in sort_key_map:
            print(f"[ERROR] Invalid sorting key '{key}'. Valid keys are: name, date, quantity, price, category.")
            return

        sort_func, label = sort_key_map[key]

        # Use custom heap sort instead of Python's built-in Timsort
        self.heap_sort(self.items, sort_func)

        print(f"\n[SUCCESS] Inventory sorted by {label} (Heap Sort)")

    # -------------------------
    # Heap Sort Implementation
    # -------------------------
    def heapify(self, arr, n, i, key_func):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n and key_func(arr[left]) > key_func(arr[largest]):
            largest = left
        if right < n and key_func(arr[right]) > key_func(arr[largest]):
            largest = right

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            self.heapify(arr, n, largest, key_func)

    def heap_sort(self, arr, key_func):
        n = len(arr)

        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            self.heapify(arr, n, i, key_func)

        # Extract elements one by one
        for i in range(n - 1, 0, -1):
            arr[i], arr[0] = arr[0], arr[i]  # swap
            self.heapify(arr, i, 0, key_func)


    def display_inventory(self, filter_path: Optional[List[str]] = None):
        """Prints the current inventory items, optionally filtered by category."""


        # POSSIBLE IMPROVEMENT  (issue #6)
        # This filters items by iterating through every stored item, which takes O(n) where
        # n = number of items. This could instead be done by navigating the category tree and adding items from there.
        # this has a worse worst case scenario, O(n) where n = nodes, but should be faster for intended use case.

        if filter_path:
            items_to_display = []
            # Find node indicated by path
            node = self.find_category_node(filter_path)
            current_node = node         # tracks current node, starting with root
            running = True              # bool for looping
            next_nodes = LinkedQueue()
            # Use a queue to implement a breadth first search, this allows us to also find items that are children
            # of other nodes on the specified path
            while running:
                for item in current_node.items:
                    items_to_display.append(item)


                for child in current_node.children:                         # add children of current node to next_nodes queue
                    next_nodes.enqueue(child)
                if next_nodes.is_empty():                           # if next_nodes is empty, entire tree has been
                    running = False                                 # searched
                else:
                    current_node = next_nodes.dequeue()


            filter_str = f" in Category: {' > '.join(filter_path)}"
        else:
            filter_str = ""
            items_to_display = self.items

        if not items_to_display:
            print(f"\n--- Inventory is Empty{filter_str} ---")
            return

        print(f"\n--- Current Inventory{filter_str} ---")
        print("=" * 110)
        print(f"{'Name':<25} {'Category Path':<30} {'Quantity':<10} {'Price':<10} {'Date Added':<30}")
        print("-" * 110)
        for item in items_to_display:
            date_str = item.date_added.strftime('%Y-%m-%d %H:%M:%S')
            category_str = ' > '.join(item.category_path) if item.category_path else 'Uncategorized'

            print(f"{item.name:<25} {category_str:<30} {item.quantity:<10} ${item.price:<9.2f} {date_str:<30}")
        print("=" * 110 + "\n")

    # --- Persistence Methods ---

    def save_inventory(self, filename: str = "inventory_data.json"):
        """Saves the current inventory and category tree to a JSON file."""
        data_to_save = {
            'items': [item.to_dict() for item in self.items],
            'categories': self.category_tree.to_dict()  # Save the category tree
        }
        try:
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print(
                f"\n[SYSTEM] Successfully saved inventory data ({len(self.items)} items) and categories to '{filename}'.")
        except IOError as e:
            print(f"\n[SYSTEM ERROR] Error saving inventory: {e}")

# Changed by Zach M. now loads inventory items into the category tree for issue #6
    def load_inventory(self, filename: str = "inventory_data.json"):
        """Loads inventory data and category tree from a JSON file."""
        try:
            with open(filename, 'r') as f:
                data_loaded = json.load(f)

            self.items.clear()

            # Load categories first
            if 'categories' in data_loaded:
                self.category_tree = CategoryNode.from_dict(data_loaded['categories'])
                print("[SYSTEM] Category tree loaded.")

            # Load items
            if 'items' in data_loaded:
                for item_data in data_loaded['items']:
                    date_obj = datetime.datetime.fromisoformat(item_data['date_added'])

                    new_item = InventoryItem(
                        name=item_data['name'],
                        quantity=item_data['quantity'],
                        price=item_data['price'],
                        date_added=date_obj,
                        # Retrieve category path, defaulting to empty list if missing for backward compatibility
                        category_path=item_data.get('category_path', [])
                    )
                    self.items.append(new_item)
                    if new_item.category_path:
                        node = self.find_category_node(new_item.category_path)
                        node.items.append(self.items[-1])


            print(f"[SYSTEM] Successfully loaded {len(self.items)} items from '{filename}'.")

        except FileNotFoundError:
            print(f"\n[SYSTEM] No save file found at '{filename}'. Starting with an empty inventory.")
        except json.JSONDecodeError:
            print(f"\n[SYSTEM ERROR] Could not decode JSON data from '{filename}'. File corrupted.")
        except Exception as e:
            print(f"\n[SYSTEM ERROR] An error occurred during loading: {e}")


# --- Helper Functions for Menu Loop ---

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
    print("7. Category Management")
    print("6. Save & Exit")
    print("-" * 40)
    return input("Enter your choice (1-7, 6 to exit): ")


def category_menu():
    """Displays the category management menu options."""
    print("\n" + "-" * 40)
    print("## CATEGORY MANAGEMENT ##")
    print("-" * 40)
    print("1. Add Category")
    print("2. View Category Tree")
    print("3. Back to Main Menu")
    print("-" * 40)
    return input("Enter your choice (1-3): ")


def get_valid_input(prompt: str, data_type: type, non_negative: bool = False, optional: bool = False) -> Optional[Any]:
    """Helper function to safely get and validate user input."""
    while True:
        user_input = input(prompt).strip()
        if optional and not user_input:
            return None
        if not user_input and not optional:
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


def get_category_path_input(prompt: str, manager: InventoryManager, required: bool = False) -> Optional[List[str]]:
    """Helper function to get and parse a category path from user input."""
    while True:
        path_str = input(prompt).strip()
        if not path_str:
            if required:
                print("[INPUT ERROR] Category path is required.")
                continue
            return []  # Returns empty list for Uncategorized

        # Split path by slashes or greater than signs
        if '>' in path_str:
            path_list = [p.strip() for p in path_str.split('>') if p.strip()]
        else:
            path_list = [p.strip() for p in path_str.split('/') if p.strip()]

        if not path_list:
            if required:
                print("[INPUT ERROR] Category path is required.")
                continue
            return []

        # Validation is handled by add_item/edit_item in the main loop for existence,
        # but we ensure the structure is correct here.
        return path_list


def category_management_loop(manager: InventoryManager):
    """Loop for category-specific actions."""
    while True:
        choice = category_menu()

        if choice == '1':
            # Add Category
            print("\n--- ADD CATEGORY ---")
            path_str = input("Enter new category path (e.g., Electronics/Laptops or Clothing>Shirts): ").strip()

            if '>' in path_str:
                path = [p.strip() for p in path_str.split('>') if p.strip()]
            else:
                path = [p.strip() for p in path_str.split('/') if p.strip()]

            manager.add_category(path)

        elif choice == '2':
            # View Category Tree
            manager.display_category_tree()

        elif choice == '3':
            # Back
            return

        else:
            print("\n[INPUT ERROR] Invalid choice. Please select a number between 1 and 3.")


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

            category_path = get_category_path_input("Enter category path (e.g., Food/Produce) - optional: ", manager,
                                                    required=False)
            quantity = get_valid_input("Enter quantity (integer): ", int, non_negative=True)
            price = get_valid_input("Enter price (float): $", float, non_negative=True)

            if name and quantity is not None and price is not None:
                try:
                    new_item = InventoryItem(name, quantity, price, category_path)
                    manager.add_item(new_item)
                except ValueError as e:
                    print(f"[ERROR] Failed to create item: {e}")

        elif choice == '2':
            # Edit Existing Item
            print("\n--- EDIT ITEM ---")
            name_to_edit = input("Enter name of item to edit: ").strip()

            # POSSIBLE IMPROVEMENT: function get_item_by_name can be improved with binary search (issue #5)
            if not manager.get_item_by_name(name_to_edit):
                print(f"[ERROR] Item '{name_to_edit}' not found.")
                continue

            print("Enter new quantity, price, or category. Press ENTER to skip a field.")

            new_quantity = get_valid_input("New quantity (integer, optional): ", int, non_negative=True, optional=True)
            new_price = get_valid_input("New price (float, optional): $", float, non_negative=True, optional=True)
            new_category_path_input = get_category_path_input("New category path (e.g., Food/Dairy) - optional: ",
                                                              manager, required=False)

            # If the user pressed enter for category, we pass None to avoid changing it.
            # If the user entered a path, it's passed as a list.
            if new_category_path_input is not None and new_category_path_input == []:
                # If user explicitly wants to remove categorization
                new_category_path = []
            elif new_category_path_input is not None:
                new_category_path = new_category_path_input
            else:
                new_category_path = None  # Do not modify category

            manager.edit_item(name_to_edit, new_quantity, new_price, new_category_path)

        elif choice == '3':
            # Remove Item
            print("\n--- REMOVE ITEM ---")
            name_to_remove = input("Enter name of item to remove: ").strip()
            manager.remove_item(name_to_remove)

        elif choice == '4':
            # Sort Inventory
            print("\n--- SORT INVENTORY ---")
            sort_key = input("Sort by (name, date, quantity, price, category): ").strip()
            manager.sort_inventory(sort_key)

        elif choice == '5':
            # Display Inventory
            print("\n--- DISPLAY INVENTORY ---")
            filter_choice = input(
                "Do you want to display (A)ll items or filter by a (C)ategory? (A/C, default A): ").strip().upper()

            filter_path_to_use = None

            if filter_choice == 'C':
                input_path = get_category_path_input("Enter category path to filter by (e.g., Food/Produce): ", manager,
                                                     required=False)

                # Check if the entered path is valid (exists in the tree)

                if input_path and not manager.find_category_node(input_path):
                    print(f"[ERROR] Category path {' > '.join(input_path)} not found. Displaying all items instead.")
                elif input_path:
                    # Use the path if it's found
                    filter_path_to_use = input_path

            manager.display_inventory(filter_path_to_use)

        elif choice == '7':
            # Category Management
            category_management_loop(manager)

        elif choice == '6':
            # Save and Exit
            print("\n--- EXITING APPLICATION ---")
            manager.save_inventory()
            break

        else:
            print("\n[INPUT ERROR] Invalid choice. Please select a number between 1 and 7 (6 to exit).")


# --- Main Entry Point ---
if __name__ == "__main__":
    run_app()
