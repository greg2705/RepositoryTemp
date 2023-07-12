def find_consecutive_duplicates_indices(lst):
    indices = []
    duplicates = set()
    for i, item in enumerate(lst):
        if i > 0 and item == lst[i - 1]:
            duplicates.add(item)
        elif item in duplicates:
            indices.append(i)
    return indices

# Example usage
my_list = [1, 2, 2, 3, 3, 1]
result = find_consecutive_duplicates_indices(my_list)
print(result)
