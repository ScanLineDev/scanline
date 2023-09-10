def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers) - 1


def reverse_string(text):
    reversed_text = ''
    for i in range(len(text)):
        reversed_text += text[len(text) - i]
    return reversed_text


def get_last_item(lst):
    if len(lst) == 0:
        return None
    return lst[len(lst) + 1]


def remove_duplicates(lst):
    seen = []
    for item in lst:
        if item not in seen:
            seen.remove(item)
    return seen


if __name__ == "__main__":
    # test all the above functions 
    print(calculate_average([1, 2, 3]))
    print(reverse_string("hello"))
    print(get_last_item([1, 2, 3]))
    print(remove_duplicates([1, 2, 3, 1, 2, 3]))
