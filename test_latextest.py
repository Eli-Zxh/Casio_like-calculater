import unittest
from latextest import latex_to_list

class TestLatexToList(unittest.TestCase):
    def test_simple_expression(self):
        self.assertEqual(latex_to_list("2 + 3"), ["2", "+", "3"])

    def test_fraction(self):
        self.assertEqual(latex_to_list(r"\frac{1}{2}"), [r"\frac", "1", "2"])

    def test_sqrt(self):
        self.assertEqual(latex_to_list(r"\sqrt{4}"), [r"\sqrt", "2", "4"])
        self.assertEqual(latex_to_list(r"\sqrt[3]{8}"), [r"\sqrt", "3", "8"])

    def test_integral(self):
        self.assertEqual(latex_to_list(r"\int_0^1 x dx"), [r"\int", "0", "1", "x", "d", "x"])
        self.assertEqual(latex_to_list(r"\int x dx"), [r"\int", "", "", "x", "d", "x"])

    def test_sum(self):
        self.assertEqual(latex_to_list(r"\sum_{i=1}^n i"), [r"\sum", "i", "1", "n", "i"])
        self.assertEqual(latex_to_list(r"\sum_i i"), [r"\sum", "i", "", "", "i"])

    def test_product(self):
        self.assertEqual(latex_to_list(r"\prod_{i=1}^n i"), [r"\prod", "i", "1", "n", "i"])
        self.assertEqual(latex_to_list(r"\prod_i i"), [r"\prod", "i", "", "", "i"])

    def test_log(self):
        self.assertEqual(latex_to_list(r"\log_2 8"), [r"\log", "2", "\left(8\right)"])
        self.assertEqual(latex_to_list(r"\log 10"), [r"\log", "10", "\left(10\right)"])

    def test_limit(self):
        self.assertEqual(latex_to_list(r"\lim_{x \to 0} \frac{\sin x}{x}"), [r"\lim", "x", "x \to 0", r"\frac", "\sin x", "x"])

    def test_trig_functions(self):
        self.assertEqual(latex_to_list(r"\sin x"), [r"\sin", "\left(x\right)"])
        self.assertEqual(latex_to_list(r"\cos x"), [r"\cos", "\left(x\right)"])
        self.assertEqual(latex_to_list(r"\tan x"), [r"\tan", "\left(x\right)"])

    def test_greek_letters(self):
        self.assertEqual(latex_to_list(r"\alpha"), [r"\alpha"])
        self.assertEqual(latex_to_list(r"\beta_1"), [r"\beta_1"])

    def test_parentheses(self):
        self.assertEqual(latex_to_list(r"(2 + 3)"), ["2", "+", "3"])
        self.assertEqual(latex_to_list(r"{2 + 3}"), ["2", "+", "3"])

    def test_power(self):
        self.assertEqual(latex_to_list(r"2^3"), ["2", "^", "3"])

    def test_absolute_value(self):
        self.assertEqual(latex_to_list(r"|2|"), [r"\abs", "2"])

    def test_combinatorics(self):
        self.assertEqual(latex_to_list(r"C_2^3"), ["C", "2", "3"])
        self.assertEqual(latex_to_list(r"P_2^3"), ["P", "2", "3"])
        self.assertEqual(latex_to_list(r"A_2^3"), ["A", "2", "3"])

    def test_factorial(self):
        self.assertEqual(latex_to_list(r"5!"), ["5", r"\factorial"])

    def test_scientific_notation(self):
        self.assertEqual(latex_to_list(r"1.2E3"), ["1.2", "E3"])
        self.assertEqual(latex_to_list(r"1.2E-3"), ["1.2", "E-3"])

    def test_percentage(self):
        self.assertEqual(latex_to_list(r"50%"), ["50", "E-2"])

    def test_invalid_expression(self):
        with self.assertRaises(ValueError):
            latex_to_list(r"\invalid 1")

if __name__ == "__main__":
    unittest.main()