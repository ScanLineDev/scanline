def is_anagram(str1, str2):
    # Logical error: Does not consider character frequency, just checks the sets
    return set(str1) == set(str2)

def calculate_discount(price, discount):
    # Logical error: Incorrectly calculates the discounted price
    return price - (price / discount)


if __name__ == "__main__":
    print(is_anagram("listen", "silent"))  # Should return True, returns True (might fail on other inputs)
    print(is_anagram("triangle", "integral"))  # Should return True, returns True (might fail on other inputs)
    print(is_anagram("aab", "abb"))  # Should return False, returns True

    print(calculate_discount(100, 10))  # Should return 90, returns 90 (might fail on other inputs)
    print(calculate_discount(200, 20))  # Should return 180, returns 190
