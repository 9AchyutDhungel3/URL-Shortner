# def square_it(nums: list[int]) -> list[int]: # here num is a list
#     result: list[int] = []
#     for i in nums:
#         result.append(i*i)
#     return result

# nums = [1,2,3,4,5]
# square_nums = square_it(nums)
# print(square_nums)
from collections.abc import Generator

def square_it(nums: list[int]) -> Generator[int]:
    for i in nums:
        yield(i*i)

nums = [1,2,3,4,5]
square_nums = square_it(nums)
print(next(square_nums))
print(next(square_nums))
print(next(square_nums))
print(next(square_nums))
print(next(square_nums))
print(next(square_nums))
print(next(square_nums))