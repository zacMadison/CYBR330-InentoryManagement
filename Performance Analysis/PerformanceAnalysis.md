# Performance Analysis
## Inventory Managers
Most tests were completed with two different inventory managers;
- Well Balanced: 5 categories, each with 2 subcategories, and with each category has 10 items stored. This represents the intended use-case scenario.
- Lopsided: Chain of 9 subcategories with only 1 category, each with 10 items stored. Represents a worst case scenario of multiple functions.
## Add Item
- New: 1000 iterations 
	- Without category: 0.12689080000018294
	- Worst case category: 0.14234550000037416
- Old: 1000 iterations
	- Without category: 0.2684326999988116
	- Worst case category: 0.27838560000054713
### Analysis
The new algorithm saves a large amount of time by replacing an O(n) search with an O(log(n)) binary search. However, this function still overall runs in O(n) due to a call to find_category_node, which runs in O(n). Ours saves time overall, being log(n) + n instead of n+n.
## Delete Item
- New
	- Well Balanced
		- Existing Item: 0.0004776999994646758
			- 100 iterations
		- Nonexistant Item: 0.0001343000003544148
			- 1000 iterations
	- Lopsided
		- Existing Item: 4.119999903196003
			- 100 iterations
		- Nonexistant Item: 0.0016116999995574588
			- 1000 iterations
- Old
	- Well Balanced
		- Existing Item: 0.00044010000056005083
			- 100 iterations
		- Nonexistant Item: 0.0001336999994236976
			- 1000 iterations
	- Lopsided
		- Existing Item: 7.669999831705354
			- 100 iterations
		- Nonexistant Item: 0.015219099999740138
			- 1000 iterations
### Analysis
The new algorithm is forced to take on aditional overhead in Delete Item. While it is able to swap a search with a binary search, that time is lost updating index of items_sorted. This overhead is necessary for efficiency gained elsewhere. Additionally, in the scenario where the item is not found time is saved by doing a binary search instead of a regular search. This function overall remains O(n), except in the case the item does not exist where is is O(log(n))
## Edit Item
- New: 1000 iterations
	- Random existant item
		- Well Balanced: 0.0017220000008819625
		- Lopsided: 0.0019572999990487006
	- Nonexistant item: 
		- Well Balanced: 0.0013917000014771475
		- Lopsided: 0.001759900000251946
- Old: 1000 iterations each
	- Random existant item
		- Well Balanced: 0.006012699999700999
		- Lopsided: 0.009918499999912456
	- Nonexistant item: 
		- Well Balanced: 0.009195900000122492
		- Lopsided: 0.014794099999562604
### Analysis
This function is reduced from O(n) to O(log(n)) through the implementation of binary search
## Inventory Display Filtered by Category
- New: 1000 iterations
	- Well Balanced: 0.22254000000066299
	- Lopsided(worst-case): 2.2612984999996115
- Old: 1000 iterations
	- Well Balanced: 0.6241042000001471
	- Lopsided(worst-case): 2.065114099999846
### Analysis
The speed complexity of this was originally O(n) where n = all items; the new algorithm is O(n) where n = nodes and items under filtered node. This is faster in reasonable scenarios, but would be slower if there are more nodes and items under the filtered node than there are items total. This is considered an improvement, because under intended use-case of an inventory managment system there should be significantly more items than categories.
## Display Categories
- New: 1000 iterations
	- Well Balanced: 0.058528500001557404
	- Lopsided: 0.05877099999997881
- Old: 1000 iterations
	- Well Balanced: 0.05644190000020899
	- Lopsided: 0.0563068999999814
### Analysis
This only change made to this was to remove recursion. This both removes the python recusion limit, and should speed up due lowered overhead. However, this has not been seen in practical testing, this is probably either caused by testing methodology or an inefficient solution
## Heap Sort
### Analysis
This implementation swapped default python sort for an implementation of heap sort. Because this is an inplace sort the additional space required is O(1), and and the time required remains the same at O(nlog(n)).