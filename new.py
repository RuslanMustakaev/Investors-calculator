def nearest_value(values: set, one: int) -> int:
    list_of_distance_and_numbers = [(abs(number - one), number) for number in values]
    return sorted(list_of_distance_and_numbers)[0][1]


print("Example:")
print(nearest_value({4, 7, 10, 11, 12, 17}, 9))
