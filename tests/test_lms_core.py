import unittest

# LMS Core circulation & search logic tests
class Book:
    def __init__(self, book_id, title, author, total_copies):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.total_copies = total_copies
        self.available_copies = total_copies

    def checkout(self):
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        return False

    def return_book(self):
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False

def calculate_overdue_fine(days_overdue, rate_per_day=0.50):
    if days_overdue <= 0:
        return 0.0
    return round(days_overdue * rate_per_day, 2)

class TestBookMatrixLMS(unittest.TestCase):
    def setUp(self):
        self.book = Book(1, "Clean Code", "Robert C. Martin", 3)

    def test_initial_availability(self):
        self.assertEqual(self.book.available_copies, 3)

    def test_checkout_and_return(self):
        self.assertTrue(self.book.checkout())
        self.assertEqual(self.book.available_copies, 2)
        self.assertTrue(self.book.return_book())
        self.assertEqual(self.book.available_copies, 3)

    def test_checkout_depletion(self):
        self.book.checkout()
        self.book.checkout()
        self.book.checkout()
        self.assertFalse(self.book.checkout()) # 0 available

    def test_overdue_fine(self):
        self.assertEqual(calculate_overdue_fine(0), 0.0)
        self.assertEqual(calculate_overdue_fine(5, 0.50), 2.50)

if __name__ == '__main__':
    unittest.main()
