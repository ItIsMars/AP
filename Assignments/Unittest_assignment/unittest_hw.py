from datetime import datetime
from decimal import Decimal
import unittest
def run_tests(test_class):
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

class Driver:
    total_drivers = 0
    company_credit = Decimal('0')

    def __init__(self, username, position):
        if not isinstance(username, str):
            raise TypeError('Invalid username type')
        if not username or not username.isalnum():
            raise ValueError('Invalid username')
        if not isinstance(position, tuple):
            raise TypeError('Invalid position type')
        if len(position) != 2:
            raise ValueError('Invalid position')
        if not all(type(x) is int for x in position):
            raise TypeError('Invalid coordinates')

        self.username = username
        self.position = position
        self.credit = Decimal('0')
        self.status = 'FREE'
        self.cost = None
        self.destination = None
        Driver.total_drivers += 1

    def assign_order(self, cost, destination):
        if self.status == 'BUSY':
            raise RuntimeError('Driver is busy')
        if not isinstance(cost, Decimal):
            raise TypeError('Invalid cost type')
        if cost <= Decimal('0'):
            raise ValueError('Cost must be positive')
        if not isinstance(destination, tuple):
            raise TypeError('Invalid destination type')
        if len(destination) != 2:
            raise ValueError('Invalid destination')
        if not all(type(x) is int for x in destination):
            raise TypeError('Invalid coordinates')

        self.cost = cost
        self.destination = destination
        self.status = 'BUSY'
        return True

    def deliver(self):
        if self.status != 'BUSY':
            raise RuntimeError('No active order')

        self.position = (self.destination[1], self.destination[0])
        self.status = 'FREE'
        self.credit += self.cost * Decimal('0.8')
        Driver.company_credit += self.cost * Decimal('0.1')
        delivery_time = datetime.now()

        return (self.username, self.position,
                self.credit, delivery_time)

import unittest
from decimal import Decimal

class TestDriver(unittest.TestCase):

    def setUp(self):
        # Keep tests independent of each other.
        Driver.total_drivers = 0
        Driver.company_credit = Decimal('0')

    def test_initial_state(self):
        # A complete example of a unit test
        driver = Driver('Ali123', (1, 2))
        self.assertEqual(driver.status, 'FREE')
        self.assertEqual(driver.credit, Decimal('0'))

    def test_behavior_1(self):
        driver = Driver('Ali123', (1, 2))
        driver.assign_order(Decimal('100'), (5, 8))

        driver.deliver()

        self.assertEqual(driver.position, (5, 8))


    def test_behavior_2(self):
        driver = Driver('Reza456', (1, 2))
        driver.assign_order(Decimal('100'), (5, 8))

        driver.deliver()

        self.assertEqual(Driver.company_credit, Decimal('20'))


    def test_boundary_or_error(self):
        driver = Driver('Sara789', (1, 2))

        with self.assertRaises(RuntimeError):
            driver.deliver()

# In the course notebook, use the existing run_tests function:
run_tests(TestDriver)

# Or, in an independent .py file, replace the line above with:
# if __name__ == '__main__':
#     unittest.main()


''' 
testing results:
test_behavior_1 (__main__.TestDriver.test_behavior_1) ... FAIL
test_behavior_2 (__main__.TestDriver.test_behavior_2) ... FAIL
test_boundary_or_error (__main__.TestDriver.test_boundary_or_error) ... ok
test_initial_state (__main__.TestDriver.test_initial_state) ... ok

======================================================================
FAIL: test_behavior_1 (__main__.TestDriver.test_behavior_1)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "d:\Programming\University\ap\HWs\unittest_hw.py", line 87, in test_behavior_1
    self.assertEqual(driver.position, (5, 8))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Tuples differ: (8, 5) != (5, 8)

First differing element 0:
8
5

- (8, 5)
+ (5, 8)

======================================================================
FAIL: test_behavior_2 (__main__.TestDriver.test_behavior_2)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "d:\Programming\University\ap\HWs\unittest_hw.py", line 96, in test_behavior_2
    self.assertEqual(Driver.company_credit, Decimal('20'))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Decimal('10.0') != Decimal('20')

----------------------------------------------------------------------
Ran 4 tests in 0.004s

FAILED (failures=2)
'''