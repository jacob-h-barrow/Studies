import time
import random
import threading
import re
import typing

from typing import Final
from concurrent.futures import ThreadPoolExecutor
from atomic_variable import AtomicVariable
from datetime import datetime

class Account:    
    @staticmethod
    def check_account_number(account_number) -> bool:
        return bool(re.fullmatch(r'\d{10}', account_number))
    
    def __init__(self, account_number: str, balance: int = 0, timeout: float=5.5):    	
        if self.check_account_number(account_number):
            self.__account_number: Final = account_number
        else:
            raise ValueError(f'{account_number} is not formatted correctly')
        
        self.__balance = max(balance, 0)
        
        self.timeout = timeout
        self.atomic_balance = AtomicVariable(value=max(balance, 0), lock=threading.RLock(), timeout=self.timeout)
        
    @property
    def account_number(self):
        return self.__account_number
        
    @property
    def balance(self):
    	return self.atomic_balance.get()
        
    @balance.setter
    def balance(self, new_amount: int):
        if (res := self.atomic_balance.set(new_amount, expected_predicate=lambda x: x > 0)) == -1:
            raise Exception('Couldnt change the balance')

type ATM_Action[**P, Date: datetime] = typing.Callable[typing.Concatenate[Date, P], bool | int]

def check_atm_use(arg) -> typing.TypeGuard[int]:
    return isinstance(arg, int)

def out_of_band_atm_use(fxn):
    def inner(*args, **kwargs):
        res = fxn(*args, **kwargs)

        if res and res < 0:
            print(f'You had a successful transaction of {inner}\n\tbut now owe {inner * 0.02} at the door!')

    return inner

        
@typing.final
class AtmBackend:
    account_numbers_used_today: typing.ClassVar[typing.Dict[str, int]] = {}
    
    @classmethod
    def add_account_number(cls, account_number: str) -> typing.NoReturn:
        cls.account_numbers[account_number] = cls.account_numbers.get(account_number, 0) + 1
        
    @classmethod
    @out_of_band_atm_use
    def act_upon(cls, account: Account, amount: int, timeout: float = 2.5, action: str='deposit') -> bool | int:
        response = False
                
        if cls.check_account(account):
            cls.add_account_number(account.account_number)
        else:
            return response

        if amount > 0:
            try:
                match action:
                    case 'deposit':
                        account.balance += amount
                        response = amount
                    case 'withdraw':
                        account.balance -= amount
                        response = -1 * amount
                    case _:
                        raise Exception(f'Cant use {action} action')
            except:
                return False

        return response
    
    @staticmethod
    def check_account(account: Account) -> typing.TypeIs[Account]:
        return isinstance(account, Account)
    
if __name__ == "__main__":
    pass
    # Use a concurrent.futures example here!