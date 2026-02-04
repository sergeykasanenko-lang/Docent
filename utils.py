from main import *
import aiogram

async def sistem_number(number):
    number = (number).replace('е', 'e').replace('k', 'к').replace('к', '000')
    number = int(float(number))

    return number


async def scor_summ(number):
    if int(number) in range(0, 1000):
        number3 = number
    if int(number) in range(1000, 999999):
        number1 = number / 1000
        number2 = round(number1)
        number3 = f'{number2} тыщ'
    if int(number) in range(1000000, 999999999):
        number1 = number / 1000000
        number2 = round(number1)
        number3 = f'{number2} млн'
    if int(number) in range(1000000000, 999999999999):
        number1 = number / 1000000000
        number2 = round(number1)
        number3 = f'{number2} млрд'
    if int(number) in range(1000000000000, 999999999999999):
        number1 = number / 1000000000000
        number2 = round(number1)
        number3 = f'{number2} трлн'
    if int(number) in range(1000000000000000, 999999999999999999):
        number1 = number / 1000000000000000
        number2 = round(number1)
        number3 = f'{number2} квдр'
    return number3