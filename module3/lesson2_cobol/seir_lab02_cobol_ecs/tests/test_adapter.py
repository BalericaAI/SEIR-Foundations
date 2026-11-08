import unittest
from decimal import Decimal
from app.server import amount, integer

class ValidationTests(unittest.TestCase):
    def test_amount(self):
        self.assertEqual(amount('100.01', 'amount'), '100.01')
        with self.assertRaises(ValueError): amount('1.001', 'amount')
        with self.assertRaises(ValueError): amount('-1', 'amount')
        with self.assertRaises(ValueError): amount('nan', 'amount')
        with self.assertRaises(ValueError): amount(True, 'amount')
    def test_limits(self):
        self.assertEqual(amount('0', 'rate', Decimal('0'), Decimal('100')), '0.00')
        with self.assertRaises(ValueError): integer(True, 'months', 1, 600)

if __name__ == '__main__': unittest.main()
