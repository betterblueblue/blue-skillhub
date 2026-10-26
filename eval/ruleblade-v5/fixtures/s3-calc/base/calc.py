def average(nums):
    return sum(nums) / len(nums)


def totals(rows):
    t = 0
    for i in range(len(rows)):
        t = t + rows[i]["amount"]
    return t
