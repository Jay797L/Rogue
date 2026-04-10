from domain.base.data.item_presets import Meat

item = Meat()

height = 28
width = 30

number_name = 3

number_category = 7

number_specification = 11

number_choice = 23

number_help = 25


print("." * (width + 2))
for i in range(height):
    string = "".center(width)
    if i == number_name:
        string = ("  " + item.name).ljust(width)
    elif i == number_category:
        string = ("  " + item.category.value).ljust(width)
    elif i == number_specification:
        string = ("  " + item.specification).ljust(width)
    elif i == number_choice:
        string = "  USE".ljust(int(width / 2)) + "ABORT  ".rjust(int(width / 2))
    elif i == number_help:
        string = "  Enter".ljust(int(width / 2)) + "Backspase  ".rjust(int(width / 2))
    print(".", string, ".", sep="")
print("." * (width + 2))
