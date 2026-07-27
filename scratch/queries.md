# Book Matrix AI Library Assistant - Query Guide

The Book Matrix AI Library Assistant operates in two modes: Online Mode (powered by Google Gemini API) and Offline Mode (a robust local fallback engine). Below is the complete catalog of questions, instructions, and topics you can ask the assistant.

---

## 1. Offline Mode (Local Engine)
When offline, the assistant uses pattern-matching to understand and answer the following queries:

### Catalog Listing Commands
Ask the assistant to list raw data from the library database:
- **List Books:** "list books", "show all books", "all books", "catalog", "show books", "list of books"
- **List Members:** "list members", "show members", "all members", "show all members", "list of members"
- **List Categories:** "list categories", "show categories", "all categories", "list of categories"
- **List Authors:** "list authors", "show authors", "all authors", "list of authors"
- **List Publishers:** "list publishers", "show publishers", "all publishers", "list of publishers"
- **List Transactions (Borrows):** "list transactions", "show transactions", "all transactions", "list borrows", "show borrows", "all borrows"

### Database Statistics & Counts
Ask about live metrics of the library:
- **Total Books & Copies:** "how many books", "total books", "number of books", "books available", "how many copies", "total copies"
- **Total Members:** "how many members", "total members", "registered members", "registered users", "number of members"
- **Active Borrows:** "how many borrowed", "currently borrowed", "borrowed books", "books currently borrowed"
- **Overdue Books:** "how many overdue", "overdue books", "number of overdue"
- **Categories/Genres Count:** "how many categories", "total categories", "what categories", "genres available"
- **Popular/Most Borrowed Books:** "most borrowed", "popular books", "top borrowed", "frequently borrowed"
- **Recently Added Books:** "newest books", "new books", "recently added", "newest added"

### Policy & Guidelines FAQ
Ask for instructions regarding library administration:
- **Borrowing Rules:** "borrow", "how to borrow", "borrow limit", "borrow policy", "due date", "fine"
- **Returning & Fines:** "return", "how to return", "late return", "renew", "late policy", "fine calculation"
- **Account & System Navigation:** "navigate", "membership", "register", "account", "reserve", "history", "rules", "faq", "help", "librarian"

### Q&A Educational Explanations (Wikipedia Integration)
The assistant can fetch live summaries from Wikipedia for general knowledge:
- **Formats:** "what is [topic]", "who is [topic]", "explain [topic]", "define [topic]", "tell me about [topic]"
- **Direct Keywords:** "antigravity", "space and time", "blockchain", "machine learning", "artificial intelligence", "philosophy", "psychology".

### Book Recommendations
Ask for curated or dynamic book suggestions:
- **General Requests:** "recommend books", "suggest books", "popular books", "best books"
- **Genre Requests:** "recommend [genre] books", "best [genre] books" (e.g., self help, business, fiction, science, technology, finance, psychology, history, philosophy, health, wellness).
- **Conversational Follow-ups:** "recommend more", "suggest others", "tell me more", "another one"

### Live Book Search & Availability
Check if a specific title is in stock:
- **Formats:** "Is [Book Title] available?", "Do you have [Book Title]?", "search for [Book Title]" (e.g., "Is Atomic Habits available?")
- **Result:** Returns Title, Author, Category, Price, Rating, Borrows, Stock, Description, Similar Books, and a Borrow Button. If missing, suggests alternatives and external links (e.g., Library Genesis).

---

## 2. Online Mode (Gemini AI Integration)
When connected to the Gemini API, the assistant functions like ChatGPT with direct access to the database. It can interpret complex natural language and run automated queries to answer:
- **Personal Status:** "How is user Bob Jones doing?"
- **Advanced Search:** "Search for business books written by Eric Ries"
- **Summaries:** "Give me our library summary stats"
- **General Queries:** Any open-ended reading question, study guide requests, or summaries of famous books.
