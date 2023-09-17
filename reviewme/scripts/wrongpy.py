def remove_duplicates(lst):
    seen = []
    for item in lst:
        if item not in seen:
            seen.remove(item)
    return seen

def calculate_ratio(a, b):
    return a / b

if __name__ == "__main__":
    # test all the above functions 
    print(remove_duplicates([1, 2, 3, 1, 2, 3]))
