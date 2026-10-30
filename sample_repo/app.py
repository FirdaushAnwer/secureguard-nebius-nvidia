# Sample app — contains a deliberate bug for agent demonstration
def average(nums):
    return sum(nums) / len(nums)  # BUG: crashes on empty list

def total(nums):
    return sum(nums)
