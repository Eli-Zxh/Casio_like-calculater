import unittest
from latextest import _setup_operators


class TestSetupOperators(unittest.TestCase):

    def test_IllegalCharacter(self):
        with self.assertRaises(ValueError):
            _setup_operators("1 + 2 # 3")

    def test_UnmatchedAbsoluteValue(self):
        with self.assertRaises(ValueError):
            _setup_operators("|1 + 2")

    def test_MatchedAbsoluteValue(self):
        result = _setup_operators("|1 + 2|")
        self.assertEqual(result, ['\\abs{1 + 2}'])

    def test_UnmatchedParentheses(self):
        with self.assertRaises(ValueError):
            _setup_operators("(1 + 2")

    def test_UnmatchedBrackets(self):
        with self.assertRaises(ValueError):
            _setup_operators("[1 + 2")

    def test_UnmatchedBraces(self):
        with self.assertRaises(ValueError):
            _setup_operators("{1 + 2")

    def test_OperatorSplitting(self):
        result = _setup_operators("1 + 2 - 3 = 4")
        self.assertEqual(result, ['1', '+', '2', '-', '3', '=', '4'])

    def test_NegativeNumberHandling(self):
        result = _setup_operators("-1 + 2")
        self.assertEqual(result, ['-', '1', '+', '2'])

    def test_OperatorStickingFix(self):
        result = _setup_operators("-\\frac{1}{2}")
        self.assertEqual(result, ['-', '\\frac{1}{2}'])

    def test_EmptyString(self):
        result = _setup_operators("")
        self.assertEqual(result, [])

    def test_SingleNumber(self):
        result = _setup_operators("123")
        self.assertEqual(result, ['123'])

    def test_ComplexExpression(self):
        result = _setup_operators("1 + (2 - 3) * [4 / {5 + 6}]")
        self.assertEqual(result, ['1', '+', '(2 - 3)', '*', '[4 / {5 + 6}]'])

    def test_NegativeInParentheses(self):
        result = _setup_operators("(1 + (-2) * 3)")
        self.assertEqual(result, ['(', '1', '+', '(-2)', '*', '3', ')'])

    def test_NegativeInBrackets(self):
        result = _setup_operators("[1 + (-2) * 3]")
        self.assertEqual(result, ['[', '1', '+', '(-2)', '*', '3', ']'])

    def test_NegativeInBraces(self):
        result = _setup_operators("{1 + (-2) * 3}")
        self.assertEqual(result, ['{', '1', '+', '(-2)', '*', '3', '}'])

if __name__ == '__main__':
    unittest.main()