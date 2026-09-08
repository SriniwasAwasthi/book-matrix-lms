# Contributing Guidelines

Thank you for your interest in contributing to **Book Matrix LMS**!

## 🚀 Architecture & Development Workflow

Book Matrix combines a Python REST API server, an SQLite relational database, and an optimized C processing layer.

1. **Clone the Repository**
   ```bash
   git clone https://github.com/SriniwasAwasthi/book-matrix-lms.git
   cd book-matrix-lms
   ```

2. **Run Backend Server**
   ```bash
   python backend/server.py
   ```

3. **Run Automated Test Suite**
   ```bash
   python -m unittest discover -s tests -p "*.py"
   ```

4. **Submit a Pull Request**
   - Follow standard Python PEP 8 conventions.
   - Use conventional commit messages (`feat:`, `fix:`, `test:`, `docs:`).
