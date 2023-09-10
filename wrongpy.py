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

if __name__ == "__main__":
    # Test the functions (these should bring out the logical inconsistencies)
    print(calculate_area_of_triangle(3, 4))  # Should return 6, returns 12

    print(get_even_numbers([1, 2, 3, 4, 5]))  # Should return [2, 4], returns [1, 3, 5]

    print(fibonacci(5))  # Should return 5, returns 7