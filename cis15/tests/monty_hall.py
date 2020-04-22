import unittest
import sys
import pexpect
import random

from . import Project, io_control


class MontyHall(Project):

    def __init__(self, *args):
        super().__init__('monty_hall.py', *args)

    def test_03_play_game(self) :
        '''I had a problem playing the Monty Hall game'''
        self.banner("Checking game play.")

        test = pexpect.spawnu(f'python3.6 "{self.projfile}"', logfile=None, encoding='utf-8')
        door = random.randrange(1, 4)
        test.sendline(str(door))
        test.sendline('stay')
        got = test.expect([pexpect.TIMEOUT, '(?i)goat', '(?i)car'], timeout=1)
        test.close()

        test = pexpect.spawnu(f'python3.6 "{self.projfile}"', logfile=None, encoding='utf-8')
        door = random.randrange(1, 4)
        test.sendline(str(door))
        test.sendline('switch')
        got = test.expect([pexpect.TIMEOUT, '(?i)goat', '(?i)car'], timeout=1)
        test.close()

    def test_4_pick_random_door_docstring(self) :
        '''You are missing a docstring in a function.'''
        self.banner('Looking for the docstring on pick_random_door()') 
        proj = self.load_file_safe(self.projfile)
        self.assertIsNotNone(proj.pick_random_door.__doc__,
                           "Your pick_random_door() function doesn't have a docstring.")

    def test_4_montys_choice_docstring(self) :
        '''You are missing a docstring in a function.''' 
        self.banner('Looking for the docstring on montys_choice()') 
        proj = self.load_file_safe(self.projfile)
        self.assertIsNotNone(proj.montys_choice.__doc__,
                           "Your montys_choice() function doesn't have a docstring.")

    def test_4_has_won_docstring(self) :
        '''You are missing a docstring in a function.''' 
        self.banner('Looking for the docstring on has_won()') 
        proj = self.load_file_safe(self.projfile)
        self.assertIsNotNone(proj.has_won.__doc__,
                           "Your has_won() function doesn't have a docstring.")

    def x_test_5_random_door(self) :
        '''Your random_door() function returned an incorrect result.'''
        self.banner('Checking the result of the pick_random_door() function.''') 
        for i in range(10) :
            doors = self.proj.pick_random_door()
            self.assertEqual(len(doors), 3, '''Your pick_random_door() function didn't return three values.''')
            trues = 0
            for door in doors :
                if type(door) != bool :
                    self.fail('''Your pick_random_door() returned a value that was not a bool.''')
                if door :
                    trues += 1
            self.assertEqual(1, trues, '''Your pick_random_door() function returned more than one True value.''') 

    def monty_is_valid(self, car, guess, monty):
        if guess == 1 and car == 1 :
            return monty == 2 or monty == 3
        elif guess == 1 and car == 2 :
            return monty == 3
        elif guess == 1 and car == 3 :
            return monty == 2 
        elif guess == 2 and car == 1 :
            return monty == 3
        elif guess == 2 and car == 2 :
            return monty == 3 or monty == 1 
        elif guess == 2 and car == 3 :
            return monty == 1 
        elif guess == 3 and car == 1 :
            return monty == 2
        elif guess == 3 and car == 2 :
            return monty == 1
        elif guess == 3 and car == 3 :
            return monty == 1 or monty == 2

    def x_test_6_montys_choice_bools(self) :
        '''Your montys_choice() function returned an incorrect result.'''
        self.banner('Checking the montys_choice() function.') 
        for guess in range(1, 4) :
            for car in range (1, 4) :
                doors = [False, False, False]
                doors[car-1] = True 
                monty = self.proj.montys_choice(*doors, guess)
                if not self.monty_is_valid(car, guess, monty) :
                    self.fail('Monty made the wrong choice:\n  I chose {} the car is behind {} and Monty opened the door {}'.format(guess, car, monty))

    def test_6_montys_choice_numbers(self) :
        '''Your montys_choice() function returned an incorrect result.'''
        self.banner('Checking the montys_choice() function.')
        proj = self.load_file_safe(self.projfile)
        with self.fail_on_input():
            for guess in range(1, 4) :
                for car in range (1, 4) :
                    monty = proj.montys_choice(car, guess)
                    if not self.monty_is_valid(car, guess, monty) :
                        self.fail('Monty made the wrong choice:\n  I chose {} the car is behind {} and Monty opened the door {}'.format(guess, car, monty))

    def ref_won(self, car, guess, choice) :
        if car == guess:
            return not choice
        else:
            return choice

    def x_test_7_has_won_bools(self) :
        '''Your has_won() function returned an incorrect result.'''
        self.banner('Checking the has_won() function.')
        with self.fail_on_input():
            for guess in range(1, 4) :
                for car in range(1, 4) :
                    doors = [False, False, False]
                    doors[car-1] = True 
                    for ss in ['stay', 'switch'] :
                        won = self.proj.has_won(*doors, guess, ss == 'switch')
                        if won != self.ref_won(car, guess, ss) :
                            self.fail("You told me I won when I should have lost. The car is behind door {}, the user initally cose door {} and then decided to {}".format(car, guess, ss))

    def ref_won_words(self, car, guess, choice):
        if car == guess:
            return choice == "stay"
        else:
            return not choice == "stay"

    def test_7_has_won_numbers(self) :
        '''Your has_won() function returned an incorrect result.'''
        self.banner('Checking the has_won() function.')
        proj = self.load_file_safe(self.projfile)
        with self.fail_on_input():
            for guess in range(1, 4):
                for car in range(1, 4):
                    for ss in ["stay", "switch"]:
                        won = proj.has_won(car, guess, ss)
                        if won != self.ref_won_words(car, guess, ss):
                            self.fail("You told me I won when I should have lost. The car is behind door {}, the user initally cose door {} and then decided to {}".format(car, guess, ss))


if __name__ == '__main__' :
    unittest.main(verbosity=0, exit=False)
