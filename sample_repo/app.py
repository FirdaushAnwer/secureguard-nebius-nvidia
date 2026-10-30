
def average(nums):
    if not nums:
        return 0  # Handles empty list (denominator = 0)
    return sum(nums) / len(nums)

def total(nums):
    return sum(nums)
