"""
BOOK MATRIX - 100 Book Seed Script
Clears existing demo books and inserts 100 curated books across 10 categories.
Run: python database/seed_books.py
"""
import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'library.db')

BOOKS = [
    # ── SELF HELP ──────────────────────────────────────────────────────────────
    ("Atomic Habits", "James Clear", "Self Help", "Avery Publishing", "978-0735211292",
     "Tiny Changes, Remarkable Results. An easy and proven way to build good habits and break bad ones.",
     4.9, 8, 10, "https://covers.openlibrary.org/b/isbn/9780735211292-L.jpg", 2018, "English", "SH-A1", 98),
    ("The 7 Habits of Highly Effective People", "Stephen R. Covey", "Self Help", "Free Press", "978-0743269513",
     "Powerful lessons in personal change. A holistic, integrated, principle-centered approach to solving personal and professional problems.",
     4.8, 6, 8, "https://covers.openlibrary.org/b/isbn/9780743269513-L.jpg", 1989, "English", "SH-A2", 91),
    ("Think and Grow Rich", "Napoleon Hill", "Self Help", "TarcherPerigee", "978-1585424337",
     "The classic bestseller that has made millionaires of thousands. The definitive guide to wealth building.",
     4.7, 5, 7, "https://covers.openlibrary.org/b/isbn/9781585424337-L.jpg", 1937, "English", "SH-A3", 87),
    ("The Power of Now", "Eckhart Tolle", "Self Help", "New World Library", "978-1577314806",
     "A guide to spiritual enlightenment. Living in the present moment to find true happiness.",
     4.7, 6, 8, "https://covers.openlibrary.org/b/isbn/9781577314806-L.jpg", 1997, "English", "SH-A4", 85),
    ("Awaken the Giant Within", "Tony Robbins", "Self Help", "Free Press", "978-0671791544",
     "How to take immediate control of your mental, emotional, physical and financial destiny.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9780671791544-L.jpg", 1991, "English", "SH-A5", 79),
    ("The Subtle Art of Not Giving a F*ck", "Mark Manson", "Self Help", "HarperOne", "978-0062457714",
     "A counterintuitive approach to living a good life. Stop trying to be positive all the time.",
     4.6, 7, 9, "https://covers.openlibrary.org/b/isbn/9780062457714-L.jpg", 2016, "English", "SH-A6", 83),
    ("Can't Hurt Me", "David Goggins", "Self Help", "Lioncrest Publishing", "978-1544512273",
     "Master your mind and defy the odds. A story of uncommon triumph through mental toughness.",
     4.8, 5, 7, "https://covers.openlibrary.org/b/isbn/9781544512273-L.jpg", 2018, "English", "SH-A7", 88),
    ("Mindset", "Carol S. Dweck", "Self Help", "Ballantine Books", "978-0345472328",
     "The new psychology of success. Learn how a simple idea about the brain profoundly affects how we lead our lives.",
     4.7, 6, 8, "https://covers.openlibrary.org/b/isbn/9780345472328-L.jpg", 2006, "English", "SH-A8", 84),
    ("The Four Agreements", "Don Miguel Ruiz", "Self Help", "Amber-Allen Publishing", "978-1878424310",
     "A practical guide to personal freedom. A Toltec Wisdom Book about personal code of conduct.",
     4.7, 5, 7, "https://covers.openlibrary.org/b/isbn/9781878424310-L.jpg", 1997, "English", "SH-A9", 82),
    ("How to Win Friends and Influence People", "Dale Carnegie", "Self Help", "Simon & Schuster", "978-0671027032",
     "The all-time classic guide to interpersonal communication and relationship building.",
     4.8, 7, 9, "https://covers.openlibrary.org/b/isbn/9780671027032-L.jpg", 1936, "English", "SH-A10", 90),

    # ── BUSINESS ───────────────────────────────────────────────────────────────
    ("Rich Dad Poor Dad", "Robert T. Kiyosaki", "Business", "Warner Books", "978-1612680194",
     "What the rich teach their kids about money that the poor and middle class do not.",
     4.9, 9, 12, "https://covers.openlibrary.org/b/isbn/9781612680194-L.jpg", 1997, "English", "BU-B1", 96),
    ("Zero to One", "Peter Thiel", "Business", "Crown Business", "978-0804139021",
     "Notes on startups, or how to build the future. The secrets of successful startup founders.",
     4.7, 6, 8, "https://covers.openlibrary.org/b/isbn/9780804139021-L.jpg", 2014, "English", "BU-B2", 86),
    ("Good to Great", "Jim Collins", "Business", "HarperBusiness", "978-0066620992",
     "Why some companies make the leap and others don't. A study of elite corporations and their management strategies.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9780066620992-L.jpg", 2001, "English", "BU-B3", 80),
    ("The Lean Startup", "Eric Ries", "Business", "Crown Business", "978-0307887894",
     "How today's entrepreneurs use continuous innovation to create radically successful businesses.",
     4.7, 6, 8, "https://covers.openlibrary.org/b/isbn/9780307887894-L.jpg", 2011, "English", "BU-B4", 85),
    ("Blue Ocean Strategy", "W. Chan Kim", "Business", "Harvard Business Review Press", "978-1591396192",
     "How to create uncontested market space and make the competition irrelevant.",
     4.5, 4, 6, "https://covers.openlibrary.org/b/isbn/9781591396192-L.jpg", 2004, "English", "BU-B5", 75),
    ("Start With Why", "Simon Sinek", "Business", "Portfolio", "978-1591846444",
     "How great leaders inspire everyone to take action. The Golden Circle philosophy of purpose-driven leadership.",
     4.7, 7, 9, "https://covers.openlibrary.org/b/isbn/9781591846444-L.jpg", 2009, "English", "BU-B6", 87),
    ("The Hard Thing About Hard Things", "Ben Horowitz", "Business", "HarperBusiness", "978-0062273208",
     "Building a business when there are no easy answers. Honest insights into the challenges of a CEO.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9780062273208-L.jpg", 2014, "English", "BU-B7", 81),
    ("Crushing It!", "Gary Vaynerchuk", "Business", "HarperBusiness", "978-0062674678",
     "How great entrepreneurs build their business and influence—and how you can too.",
     4.5, 4, 6, "https://covers.openlibrary.org/b/isbn/9780062674678-L.jpg", 2018, "English", "BU-B8", 72),
    ("Built to Last", "Jim Collins", "Business", "HarperBusiness", "978-0060516406",
     "Successful habits of visionary companies. A study of enduring great companies.",
     4.5, 4, 6, "https://covers.openlibrary.org/b/isbn/9780060516406-L.jpg", 1994, "English", "BU-B9", 74),
    ("Rework", "Jason Fried", "Business", "Crown Business", "978-0307463746",
     "A business book for people who don't like business books. Simple, unconventional wisdom.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9780307463746-L.jpg", 2010, "English", "BU-B10", 78),

    # ── FICTION ────────────────────────────────────────────────────────────────
    ("The Alchemist", "Paulo Coelho", "Fiction", "HarperOne", "978-0062315007",
     "A mystical story about following your dreams. Santiago's legendary journey to find treasure.",
     4.8, 10, 12, "https://covers.openlibrary.org/b/isbn/9780062315007-L.jpg", 1988, "English", "FI-C1", 95),
    ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "Fiction", "Scholastic", "978-0590353427",
     "The boy who lived. The magical beginning of the most beloved fantasy series of all time.",
     4.9, 8, 10, "https://covers.openlibrary.org/b/isbn/9780590353427-L.jpg", 1997, "English", "FI-C2", 99),
    ("The Hobbit", "J.R.R. Tolkien", "Fiction", "Houghton Mifflin", "978-0547928227",
     "There and back again. The adventure of Bilbo Baggins in the world of Middle-earth.",
     4.9, 7, 9, "https://covers.openlibrary.org/b/isbn/9780547928227-L.jpg", 1937, "English", "FI-C3", 97),
    ("To Kill a Mockingbird", "Harper Lee", "Fiction", "J. B. Lippincott & Co.", "978-0061935466",
     "A Pulitzer Prize-winning masterwork of honor and injustice in the deep South.",
     4.8, 6, 8, "https://covers.openlibrary.org/b/isbn/9780061935466-L.jpg", 1960, "English", "FI-C4", 93),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", "Scribner", "978-0743273565",
     "A story of the fabulously wealthy Jay Gatsby and his love for Daisy Buchanan in 1920s America.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9780743273565-L.jpg", 1925, "English", "FI-C5", 83),
    ("1984", "George Orwell", "Fiction", "Signet Classic", "978-0451524935",
     "A dystopian social science fiction novel. Big Brother is watching you in a totalitarian society.",
     4.8, 7, 9, "https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg", 1949, "English", "FI-C6", 92),
    ("The Catcher in the Rye", "J.D. Salinger", "Fiction", "Little Brown", "978-0316769174",
     "Holden Caulfield's seminal coming-of-age story. A landmark of American literature.",
     4.5, 5, 7, "https://covers.openlibrary.org/b/isbn/9780316769174-L.jpg", 1951, "English", "FI-C7", 76),
    ("Pride and Prejudice", "Jane Austen", "Fiction", "Penguin Classics", "978-0141439518",
     "Elizabeth Bennet and Mr. Darcy in a classic romantic novel of manners set in Georgian England.",
     4.8, 6, 8, "https://covers.openlibrary.org/b/isbn/9780141439518-L.jpg", 1813, "English", "FI-C8", 91),
    ("The Kite Runner", "Khaled Hosseini", "Fiction", "Riverhead Books", "978-1594480003",
     "A story of fathers and sons, of friendship and betrayal, set against the turbulent history of Afghanistan.",
     4.7, 6, 8, "https://covers.openlibrary.org/b/isbn/9781594480003-L.jpg", 2003, "English", "FI-C9", 86),
    ("Life of Pi", "Yann Martel", "Fiction", "Mariner Books", "978-0156027328",
     "A miraculous, fable-like novel about a young man surviving 227 days at sea with a Bengal tiger.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9780156027328-L.jpg", 2001, "English", "FI-C10", 81),

    # ── SCIENCE ────────────────────────────────────────────────────────────────
    ("A Brief History of Time", "Stephen Hawking", "Science", "Bantam Books", "978-0553380163",
     "From the Big Bang to Black Holes. A landmark volume in science writing, accessible to all.",
     4.8, 7, 9, "https://covers.openlibrary.org/b/isbn/9780553380163-L.jpg", 1988, "English", "SC-D1", 93),
    ("Cosmos", "Carl Sagan", "Science", "Ballantine Books", "978-0345539434",
     "A personal voyage through the universe. The companion to Carl Sagan's legendary television series.",
     4.8, 5, 7, "https://covers.openlibrary.org/b/isbn/9780345539434-L.jpg", 1980, "English", "SC-D2", 90),
    ("Astrophysics for People in a Hurry", "Neil deGrasse Tyson", "Science", "W. W. Norton", "978-0393609394",
     "Essential pockets of knowledge about the universe for the curious but time-pressed reader.",
     4.6, 6, 8, "https://covers.openlibrary.org/b/isbn/9780393609394-L.jpg", 2017, "English", "SC-D3", 82),
    ("The Elegant Universe", "Brian Greene", "Science", "W. W. Norton", "978-0393058581",
     "Superstrings, hidden dimensions, and the quest for the ultimate theory of everything.",
     4.5, 4, 6, "https://covers.openlibrary.org/b/isbn/9780393058581-L.jpg", 1999, "English", "SC-D4", 75),
    ("The Selfish Gene", "Richard Dawkins", "Science", "Oxford University Press", "978-0198788607",
     "The gene's-eye view of evolution. The landmark book that introduced the idea of the 'meme'.",
     4.7, 5, 7, "https://covers.openlibrary.org/b/isbn/9780198788607-L.jpg", 1976, "English", "SC-D5", 83),
    ("The Gene", "Siddhartha Mukherjee", "Science", "Scribner", "978-1476733524",
     "An intimate history of how genetics shapes human biology, from Mendel to CRISPR.",
     4.7, 4, 6, "https://covers.openlibrary.org/b/isbn/9781476733524-L.jpg", 2016, "English", "SC-D6", 80),
    ("Silent Spring", "Rachel Carson", "Science", "Houghton Mifflin", "978-0618249060",
     "The landmark book that launched the environmental movement by documenting DDT's effects.",
     4.7, 4, 6, "https://covers.openlibrary.org/b/isbn/9780618249060-L.jpg", 1962, "English", "SC-D7", 77),
    ("The Origin of Species", "Charles Darwin", "Science", "Penguin Classics", "978-0140432053",
     "The foundation of evolutionary biology. Darwin's revolutionary theory of natural selection.",
     4.7, 5, 7, "https://covers.openlibrary.org/b/isbn/9780140432053-L.jpg", 1859, "English", "SC-D8", 79),
    ("Brief Answers to the Big Questions", "Stephen Hawking", "Science", "Bantam Books", "978-1984819192",
     "Stephen Hawking's final book. His thoughts on the biggest questions facing humankind.",
     4.7, 6, 8, "https://covers.openlibrary.org/b/isbn/9781984819192-L.jpg", 2018, "English", "SC-D9", 84),
    ("The Fabric of the Cosmos", "Brian Greene", "Science", "Knopf", "978-0375412882",
     "Space, time, and the texture of reality. An exploration of the cutting edge of physics.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9780375412882-L.jpg", 2004, "English", "SC-D10", 76),

    # ── TECHNOLOGY ─────────────────────────────────────────────────────────────
    ("Deep Work", "Cal Newport", "Technology", "Grand Central Publishing", "978-1455586691",
     "Rules for focused success in a distracted world. The superpower of the 21st century.",
     4.8, 8, 10, "https://covers.openlibrary.org/b/isbn/9781455586691-L.jpg", 2016, "English", "TE-E1", 92),
    ("Clean Code", "Robert C. Martin", "Technology", "Prentice Hall", "978-0132350884",
     "A handbook of agile software craftsmanship. The bible of writing clean, readable, maintainable code.",
     4.7, 6, 8, "https://covers.openlibrary.org/b/isbn/9780132350884-L.jpg", 2008, "English", "TE-E2", 87),
    ("The Pragmatic Programmer", "David Thomas", "Technology", "Addison-Wesley", "978-0201616224",
     "From journeyman to master. The classic guide to software development best practices.",
     4.7, 5, 7, "https://covers.openlibrary.org/b/isbn/9780201616224-L.jpg", 1999, "English", "TE-E3", 84),
    ("Code Complete", "Steve McConnell", "Technology", "Microsoft Press", "978-0735619678",
     "A practical handbook of software construction. The comprehensive reference for software development.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9780735619678-L.jpg", 2004, "English", "TE-E4", 78),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "Technology", "O'Reilly Media", "978-1449373320",
     "The big ideas behind reliable, scalable, and maintainable systems.",
     4.8, 5, 7, "https://covers.openlibrary.org/b/isbn/9781449373320-L.jpg", 2017, "English", "TE-E5", 91),
    ("Introduction to Algorithms", "Thomas H. Cormen", "Technology", "MIT Press", "978-0262033848",
     "The definitive reference for algorithms. Used by universities worldwide as the standard textbook.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9780262033848-L.jpg", 2009, "English", "TE-E6", 76),
    ("Artificial Intelligence: A Modern Approach", "Stuart Russell", "Technology", "Pearson", "978-0136042594",
     "The most comprehensive, up-to-date introduction to the theory and practice of artificial intelligence.",
     4.7, 5, 7, "https://covers.openlibrary.org/b/isbn/9780136042594-L.jpg", 2020, "English", "TE-E7", 85),
    ("The Phoenix Project", "Gene Kim", "Technology", "IT Revolution Press", "978-1942788294",
     "A novel about IT, DevOps, and helping your business win. The story of a manufacturing IT manager.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9781942788294-L.jpg", 2013, "English", "TE-E8", 79),
    ("Cracking the Coding Interview", "Gayle Laakmann McDowell", "Technology", "CareerCup", "978-0984782857",
     "189 programming questions and solutions. The leading guide to landing a software engineering job.",
     4.7, 6, 8, "https://covers.openlibrary.org/b/isbn/9780984782857-L.jpg", 2015, "English", "TE-E9", 88),
    ("Head First Design Patterns", "Eric Freeman", "Technology", "O'Reilly Media", "978-0596007126",
     "A brain-friendly guide to building extensible and maintainable object-oriented software.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9780596007126-L.jpg", 2004, "English", "TE-E10", 77),

    # ── FINANCE ────────────────────────────────────────────────────────────────
    ("The Psychology of Money", "Morgan Housel", "Finance", "Harriman House", "978-0857197689",
     "Timeless lessons on wealth, greed, and happiness. How money really works and how to think about it.",
     4.9, 9, 11, "https://covers.openlibrary.org/b/isbn/9780857197689-L.jpg", 2020, "English", "FN-F1", 97),
    ("The Intelligent Investor", "Benjamin Graham", "Finance", "HarperBusiness", "978-0060555665",
     "The definitive book on value investing. The bible of the stock market for Warren Buffett.",
     4.8, 7, 9, "https://covers.openlibrary.org/b/isbn/9780060555665-L.jpg", 1949, "English", "FN-F2", 93),
    ("Common Stocks and Uncommon Profits", "Philip A. Fisher", "Finance", "Wiley", "978-0471445500",
     "A timeless guide to investing based on company research and management quality.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9780471445500-L.jpg", 1958, "English", "FN-F3", 77),
    ("One Up On Wall Street", "Peter Lynch", "Finance", "Simon & Schuster", "978-0743200400",
     "How to use what you already know to make money in the market by the legendary fund manager.",
     4.7, 5, 7, "https://covers.openlibrary.org/b/isbn/9780743200400-L.jpg", 1989, "English", "FN-F4", 82),
    ("Your Money or Your Life", "Vicki Robin", "Finance", "Penguin Books", "978-0143115762",
     "9 steps to transforming your relationship with money and achieving financial independence.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9780143115762-L.jpg", 1992, "English", "FN-F5", 75),
    ("The Millionaire Next Door", "Thomas J. Stanley", "Finance", "Taylor Trade Publishing", "978-1589795471",
     "The surprising secrets of America's wealthy. How ordinary people accumulate extraordinary wealth.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9781589795471-L.jpg", 1996, "English", "FN-F6", 78),
    ("I Will Teach You to Be Rich", "Ramit Sethi", "Finance", "Workman Publishing", "978-0761147480",
     "A 6-week personal finance program for 20-somethings. No guilt, no judgment—just action.",
     4.7, 6, 8, "https://covers.openlibrary.org/b/isbn/9780761147480-L.jpg", 2009, "English", "FN-F7", 83),
    ("The Richest Man in Babylon", "George S. Clason", "Finance", "Penguin Books", "978-0451205360",
     "Ancient wisdom for wealth building. Parables set in ancient Babylon to teach financial principles.",
     4.8, 7, 9, "https://covers.openlibrary.org/b/isbn/9780451205360-L.jpg", 1926, "English", "FN-F8", 89),
    ("Money: Master the Game", "Tony Robbins", "Finance", "Simon & Schuster", "978-1476757803",
     "7 simple steps to financial freedom. Insights from 50+ of the world's greatest investors.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9781476757803-L.jpg", 2014, "English", "FN-F9", 79),
    ("Unshakeable", "Tony Robbins", "Finance", "Simon & Schuster", "978-1501164583",
     "Your financial freedom playbook. Practical strategies to protect yourself from market volatility.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9781501164583-L.jpg", 2017, "English", "FN-F10", 74),

    # ── PSYCHOLOGY ─────────────────────────────────────────────────────────────
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Psychology", "Farrar Straus Giroux", "978-0374533557",
     "The two systems that drive the way we think. System 1 and System 2 and how they shape our judgments.",
     4.7, 7, 9, "https://covers.openlibrary.org/b/isbn/9780374533557-L.jpg", 2011, "English", "PS-G1", 90),
    ("Influence", "Robert B. Cialdini", "Psychology", "HarperBusiness", "978-0062937650",
     "The psychology of persuasion. The classic book on the science of compliance and influence.",
     4.8, 6, 8, "https://covers.openlibrary.org/b/isbn/9780062937650-L.jpg", 1984, "English", "PS-G2", 91),
    ("Predictably Irrational", "Dan Ariely", "Psychology", "HarperCollins", "978-0061353246",
     "The hidden forces that shape our decisions. Why we are far less rational than we think.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9780061353246-L.jpg", 2008, "English", "PS-G3", 80),
    ("Emotional Intelligence", "Daniel Goleman", "Psychology", "Bantam Books", "978-0553383713",
     "Why it can matter more than IQ. A landmark book on the role of emotions in leadership and life.",
     4.7, 6, 8, "https://covers.openlibrary.org/b/isbn/9780553383713-L.jpg", 1995, "English", "PS-G4", 85),
    ("Man's Search for Meaning", "Viktor E. Frankl", "Psychology", "Beacon Press", "978-0807014271",
     "A harrowing and yet profoundly optimistic account of a Holocaust survivor's experiences.",
     4.9, 7, 9, "https://covers.openlibrary.org/b/isbn/9780807014271-L.jpg", 1946, "English", "PS-G5", 95),
    ("Drive", "Daniel H. Pink", "Psychology", "Riverhead Books", "978-1594484803",
     "The surprising truth about what motivates us. Intrinsic motivation vs. extrinsic rewards.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9781594484803-L.jpg", 2009, "English", "PS-G6", 79),
    ("Flow", "Mihaly Csikszentmihalyi", "Psychology", "Harper Perennial", "978-0061339202",
     "The psychology of optimal experience. Finding flow in everyday activities for a fulfilling life.",
     4.7, 4, 6, "https://covers.openlibrary.org/b/isbn/9780061339202-L.jpg", 1990, "English", "PS-G7", 81),
    ("The Lucifer Effect", "Philip Zimbardo", "Psychology", "Random House", "978-1400064113",
     "Understanding how good people turn evil. Insights from the Stanford Prison Experiment.",
     4.5, 4, 6, "https://covers.openlibrary.org/b/isbn/9781400064113-L.jpg", 2007, "English", "PS-G8", 72),
    ("Games People Play", "Eric Berne", "Psychology", "Ballantine Books", "978-0345410030",
     "The basic handbook of transactional analysis. How humans interact in social and psychological games.",
     4.4, 3, 5, "https://covers.openlibrary.org/b/isbn/9780345410030-L.jpg", 1964, "English", "PS-G9", 66),
    ("The Body Keeps the Score", "Bessel van der Kolk", "Psychology", "Viking", "978-0670785933",
     "Brain, mind, and body in the healing of trauma. A groundbreaking study of PTSD.",
     4.8, 6, 8, "https://covers.openlibrary.org/b/isbn/9780670785933-L.jpg", 2014, "English", "PS-G10", 89),

    # ── HISTORY ────────────────────────────────────────────────────────────────
    ("Sapiens", "Yuval Noah Harari", "History", "Harper", "978-0062316097",
     "A brief history of humankind. From the Stone Age to the 21st century, a sweeping history of our species.",
     4.7, 10, 12, "https://covers.openlibrary.org/b/isbn/9780062316097-L.jpg", 2011, "English", "HI-H1", 94),
    ("Guns, Germs, and Steel", "Jared Diamond", "History", "W. W. Norton", "978-0393317558",
     "The fates of human societies. Why Western civilization came to dominate the world.",
     4.6, 6, 8, "https://covers.openlibrary.org/b/isbn/9780393317558-L.jpg", 1997, "English", "HI-H2", 82),
    ("The Silk Roads", "Peter Frankopan", "History", "Knopf", "978-1101912379",
     "A new history of the world. How trade routes shaped civilizations from Persia to China.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9781101912379-L.jpg", 2015, "English", "HI-H3", 79),
    ("Team of Rivals", "Doris Kearns Goodwin", "History", "Simon & Schuster", "978-0684824901",
     "The political genius of Abraham Lincoln. How he assembled a cabinet from his enemies.",
     4.7, 4, 6, "https://covers.openlibrary.org/b/isbn/9780684824901-L.jpg", 2005, "English", "HI-H4", 80),
    ("The Wright Brothers", "David McCullough", "History", "Simon & Schuster", "978-1476728742",
     "The dramatic story-behind-the-story of the Wright Brothers and the first successful powered airplane.",
     4.7, 4, 6, "https://covers.openlibrary.org/b/isbn/9781476728742-L.jpg", 2015, "English", "HI-H5", 78),
    ("SPQR", "Mary Beard", "History", "Liveright Publishing", "978-0871404237",
     "A history of ancient Rome. The people, culture, and politics of the Roman Empire.",
     4.5, 3, 5, "https://covers.openlibrary.org/b/isbn/9780871404237-L.jpg", 2015, "English", "HI-H6", 71),
    ("The Diary of a Young Girl", "Anne Frank", "History", "Bantam Books", "978-0553296983",
     "Anne Frank's diary from 1942 to 1944. One of the most moving accounts of the Holocaust.",
     4.9, 7, 9, "https://covers.openlibrary.org/b/isbn/9780553296983-L.jpg", 1947, "English", "HI-H7", 97),
    ("A People's History of the United States", "Howard Zinn", "History", "Harper Perennial", "978-0062397348",
     "History told from the perspective of the American people — not their leaders.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9780062397348-L.jpg", 1980, "English", "HI-H8", 77),
    ("The Lessons of History", "Will Durant", "History", "Simon & Schuster", "978-1439149959",
     "A concise survey of the culture and civilization of mankind. 100 pages of pure wisdom.",
     4.7, 4, 6, "https://covers.openlibrary.org/b/isbn/9781439149959-L.jpg", 1968, "English", "HI-H9", 83),
    ("The Rise and Fall of the Third Reich", "William L. Shirer", "History", "Simon & Schuster", "978-1451651683",
     "A history of Nazi Germany. The definitive chronicle of Hitler's rise to power and eventual defeat.",
     4.8, 3, 5, "https://covers.openlibrary.org/b/isbn/9781451651683-L.jpg", 1960, "English", "HI-H10", 86),

    # ── PHILOSOPHY ─────────────────────────────────────────────────────────────
    ("Meditations", "Marcus Aurelius", "Philosophy", "Modern Library", "978-0812968255",
     "The private thoughts of Rome's greatest emperor. Timeless Stoic wisdom for daily life.",
     4.9, 8, 10, "https://covers.openlibrary.org/b/isbn/9780812968255-L.jpg", 180, "English", "PH-I1", 96),
    ("Beyond Good and Evil", "Friedrich Nietzsche", "Philosophy", "Vintage", "978-0679724650",
     "Prelude to a philosophy of the future. Nietzsche's critique of traditional morality.",
     4.5, 4, 6, "https://covers.openlibrary.org/b/isbn/9780679724650-L.jpg", 1886, "English", "PH-I2", 73),
    ("The Republic", "Plato", "Philosophy", "Oxford University Press", "978-0192833754",
     "Plato's masterwork on justice, beauty, equality, politics, and the ideal state.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9780192833754-L.jpg", -380, "English", "PH-I3", 75),
    ("Nicomachean Ethics", "Aristotle", "Philosophy", "Hackett Publishing", "978-0872204645",
     "Aristotle's treatise on the nature of virtue and the good life. The foundation of moral philosophy.",
     4.5, 3, 5, "https://covers.openlibrary.org/b/isbn/9780872204645-L.jpg", -350, "English", "PH-I4", 70),
    ("The Art of War", "Sun Tzu", "Philosophy", "Shambhala", "978-1590302255",
     "The ancient Chinese military treatise. Timeless strategies for conflict and leadership.",
     4.7, 7, 9, "https://covers.openlibrary.org/b/isbn/9781590302255-L.jpg", -500, "English", "PH-I5", 88),
    ("Tao Te Ching", "Lao Tzu", "Philosophy", "Harper Perennial", "978-0061142666",
     "The book of the way. Ancient Chinese wisdom on living in harmony with the natural order.",
     4.7, 5, 7, "https://covers.openlibrary.org/b/isbn/9780061142666-L.jpg", -600, "English", "PH-I6", 85),
    ("Thus Spoke Zarathustra", "Friedrich Nietzsche", "Philosophy", "Penguin Classics", "978-0140441185",
     "Nietzsche's masterpiece on the Overman, the will to power, and eternal recurrence.",
     4.5, 3, 5, "https://covers.openlibrary.org/b/isbn/9780140441185-L.jpg", 1883, "English", "PH-I7", 72),
    ("The Prince", "Niccolò Machiavelli", "Philosophy", "Penguin Classics", "978-0140449150",
     "The classic treatise on political power, statecraft, and leadership from Renaissance Florence.",
     4.5, 5, 7, "https://covers.openlibrary.org/b/isbn/9780140449150-L.jpg", 1532, "English", "PH-I8", 76),
    ("Critique of Pure Reason", "Immanuel Kant", "Philosophy", "Cambridge University Press", "978-0521657297",
     "Kant's groundbreaking inquiry into the nature of human knowledge and the limits of reason.",
     4.4, 3, 5, "https://covers.openlibrary.org/b/isbn/9780521657297-L.jpg", 1781, "English", "PH-I9", 65),
    ("Letters from a Stoic", "Seneca", "Philosophy", "Penguin Classics", "978-0140442106",
     "Moral epistles by the great Stoic philosopher. Practical wisdom on life, death, and virtue.",
     4.8, 5, 7, "https://covers.openlibrary.org/b/isbn/9780140442106-L.jpg", 65, "English", "PH-I10", 87),

    # ── HEALTH & WELLNESS ──────────────────────────────────────────────────────
    ("Ikigai", "Héctor García", "Health & Wellness", "Penguin Books", "978-0143130727",
     "The Japanese secret to a long and happy life. Finding your purpose at the intersection of passion and purpose.",
     4.7, 9, 11, "https://covers.openlibrary.org/b/isbn/9780143130727-L.jpg", 2016, "English", "HW-J1", 91),
    ("Why We Sleep", "Matthew Walker", "Health & Wellness", "Scribner", "978-1501144318",
     "Unlocking the power of sleep and dreams. The science of sleep and its importance for health.",
     4.7, 7, 9, "https://covers.openlibrary.org/b/isbn/9781501144318-L.jpg", 2017, "English", "HW-J2", 88),
    ("The Blue Zones", "Dan Buettner", "Health & Wellness", "National Geographic", "978-1426204401",
     "Lessons for living longer from the people who've lived the longest. The 9 habits of centenarians.",
     4.5, 5, 7, "https://covers.openlibrary.org/b/isbn/9781426204401-L.jpg", 2008, "English", "HW-J3", 76),
    ("Eat to Live", "Joel Fuhrman", "Health & Wellness", "Little Brown", "978-0316120913",
     "The amazing nutrient-rich program for fast and sustained weight loss and optimal health.",
     4.5, 4, 6, "https://covers.openlibrary.org/b/isbn/9780316120913-L.jpg", 2003, "English", "HW-J4", 72),
    ("Spark", "John J. Ratey", "Health & Wellness", "Little Brown", "978-0316113519",
     "The revolutionary new science of exercise and the brain. How physical activity boosts mental health.",
     4.6, 4, 6, "https://covers.openlibrary.org/b/isbn/9780316113519-L.jpg", 2008, "English", "HW-J5", 77),
    ("Outlive", "Peter Attia", "Health & Wellness", "Harmony", "978-0593236598",
     "The science and art of longevity. A new approach to living a long, healthy, fulfilling life.",
     4.8, 6, 8, "https://covers.openlibrary.org/b/isbn/9780593236598-L.jpg", 2023, "English", "HW-J6", 90),
    ("The China Study", "T. Colin Campbell", "Health & Wellness", "BenBella Books", "978-1932100662",
     "The most comprehensive study of nutrition ever conducted. Startling implications for diet and health.",
     4.4, 3, 5, "https://covers.openlibrary.org/b/isbn/9781932100662-L.jpg", 2004, "English", "HW-J7", 66),
    ("Breath", "James Nestor", "Health & Wellness", "Riverhead Books", "978-0735213616",
     "The new science of a lost art. How the way we breathe has changed, and what we can do about it.",
     4.6, 5, 7, "https://covers.openlibrary.org/b/isbn/9780735213616-L.jpg", 2020, "English", "HW-J8", 79),
    ("Younger Next Year", "Chris Crowley", "Health & Wellness", "Workman Publishing", "978-0761147732",
     "Live strong, fit, and sexy until you're 80 and beyond. The science behind active aging.",
     4.5, 3, 5, "https://covers.openlibrary.org/b/isbn/9780761147732-L.jpg", 2004, "English", "HW-J9", 70),
    ("The Longevity Diet", "Valter Longo", "Health & Wellness", "Avery Publishing", "978-0525534075",
     "Discover the new science behind stem cell activation and regeneration to slow aging and fight disease.",
     4.5, 4, 6, "https://covers.openlibrary.org/b/isbn/9780525534075-L.jpg", 2018, "English", "HW-J10", 73),
]

def seed_books():
    if not os.path.exists(DB_FILE):
        print(f"ERROR: Database not found at {DB_FILE}")
        print("Please start the server first to initialize the database.")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Ensure new columns exist
    c.execute("PRAGMA table_info(books)")
    cols = [r[1] for r in c.fetchall()]
    migrations = [
        ("isbn", "TEXT DEFAULT ''"),
        ("cover_image", "TEXT DEFAULT ''"),
        ("published_year", "INTEGER DEFAULT 2020"),
        ("language", "TEXT DEFAULT 'English'"),
        ("shelf_location", "TEXT DEFAULT 'A1'"),
        ("date_added", "TEXT DEFAULT '2026-01-01'"),
        ("status", "TEXT DEFAULT 'Active'"),
        ("popularity_score", "INTEGER DEFAULT 50"),
        ("rating", "REAL DEFAULT 4.5"),
        ("borrow_count", "INTEGER DEFAULT 0"),
    ]
    for col, defn in migrations:
        if col not in cols:
            c.execute(f"ALTER TABLE books ADD COLUMN {col} {defn}")
            print(f"  Added column: {col}")

    # Remove all existing demo/seed books (keep user-added ones with transactions)
    c.execute("""
        DELETE FROM books WHERE id NOT IN (
            SELECT DISTINCT book_id FROM transactions
        )
    """)
    deleted = conn.total_changes
    print(f"  Removed {deleted} demo books (books with active transactions preserved)")

    # Insert all 100 books
    insert_sql = """
        INSERT INTO books
            (title, author, category, publisher, isbn, description, rating,
             available_quantity, total_quantity, cover_image, published_year,
             language, shelf_location, status, popularity_score,
             borrow_count, price, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?, ?, 0.00, date('now'))
    """

    inserted = 0
    for book in BOOKS:
        title, author, cat, pub, isbn, desc, rating, avail, total, cover, year, lang, shelf, pop = book
        try:
            c.execute(insert_sql, (title, author, cat, pub, isbn, desc, rating,
                                   avail, total, cover, year, lang, shelf, pop, 0))
            inserted += 1
        except Exception as e:
            print(f"  WARN: Could not insert '{title}': {e}")

    conn.commit()
    conn.close()
    print(f"\nSUCCESS: Seeded {inserted} books across 10 categories!")
    print("   Categories: Self Help, Business, Fiction, Science, Technology,")
    print("               Finance, Psychology, History, Philosophy, Health & Wellness")

if __name__ == "__main__":
    seed_books()
