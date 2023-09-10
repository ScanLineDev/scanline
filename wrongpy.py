def calculate_area_of_triangle(base, height):
    # Logical error: Should return 0.5 * base * height, not base * height
    return base * height

def get_even_numbers(numbers):
    # Logical error: Returns odd numbers instead of even numbers
    return [n for n in numbers if n % 2 != 0]

def fibonacci(n):
    # Logical error: Incorrect implementation of the Fibonacci sequence
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2) + 1  # Incorrect '+ 1'

def is_anagram(str1, str2):
    # Logical error: Does not consider character frequency, just checks the sets
    return set(str1) == set(str2)

def calculate_discount(price, discount):
    # Logical error: Incorrectly calculates the discounted price
    return price - (price / discount)

if __name__ == "__main__":
    # Test the functions (these should bring out the logical inconsistencies)
    print(calculate_area_of_triangle(3, 4))  # Should return 6, returns 12

    print(get_even_numbers([1, 2, 3, 4, 5]))  # Should return [2, 4], returns [1, 3, 5]

    print(fibonacci(5))  # Should return 5, returns 7

    print(is_anagram("listen", "silent"))  # Should return True, returns True (might fail on other inputs)
    print(is_anagram("triangle", "integral"))  # Should return True, returns True (might fail on other inputs)
    print(is_anagram("aab", "abb"))  # Should return False, returns True

    print(calculate_discount(100, 10))  # Should return 90, returns 90 (might fail on other inputs)
    print(calculate_discount(200, 20))  # Should return 180, returns 190
