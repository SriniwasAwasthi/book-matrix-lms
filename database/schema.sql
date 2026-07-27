-- Library Management System Schema (v2)
-- Includes Categories, Publishers, and comprehensive data

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT DEFAULT 'Uncategorized',
    publisher TEXT DEFAULT 'Unknown',
    price REAL NOT NULL,
    description TEXT,
    total_quantity INTEGER NOT NULL,
    available_quantity INTEGER NOT NULL,
    rating REAL DEFAULT 4.5,
    borrow_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    issue_date DATE NOT NULL,
    return_date DATE NOT NULL,
    actual_return_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- Insert Sample Users
INSERT INTO users (name, email) VALUES 
('Alice Smith', 'alice@example.com'), 
('Bob Jones', 'bob@example.com'),
('Charlie Brown', 'charlie.b@gmail.com'),
('Diana Prince', 'diana.p@gmail.com'),
('Ethan Hunt', 'ethan.h@gmail.com'),
('Fiona Gallagher', 'fiona.g@gmail.com'),
('George Miller', 'george.m@gmail.com');

-- Insert Books with Categories
INSERT INTO books (title, author, category, publisher, price, description, total_quantity, available_quantity) VALUES
-- Classic & Fiction
('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 'Scribner', 15.99, 'Classic American novel set in the Jazz Age.', 5, 5),
('1984', 'George Orwell', 'Fiction', 'Secker & Warburg', 12.50, 'Dystopian novel about surveillance and totalitarianism.', 3, 3),
('Brave New World', 'Aldous Huxley', 'Fiction', 'Chatto & Windus', 14.20, 'A futuristic society shaped by technology and control.', 4, 4),
('The Alchemist', 'Paulo Coelho', 'Philosophy', 'HarperOne', 15.00, 'A philosophical novel about destiny and dreams.', 50, 50),

-- Psychology & Self-Help
('Atomic Habits', 'James Clear', 'Self-Help', 'Avery', 20.00, 'Build good habits and break bad ones.', 10, 10),
('Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology', 'Farrar, Straus and Giroux', 22.50, 'Exploration of human decision-making and biases.', 15, 15),
('Mindset', 'Carol S. Dweck', 'Psychology', 'Ballantine Books', 18.00, 'The power of a growth mindset.', 12, 12),
('Deep Work', 'Cal Newport', 'Productivity', 'Grand Central Publishing', 21.00, 'Rules for focused success in a distracted world.', 8, 8),
('Man''s Search for Meaning', 'Viktor E. Frankl', 'Psychology', 'Beacon Press', 14.50, 'A memoir and psychological exploration of purpose.', 20, 20),
('The Power of Habit', 'Charles Duhigg', 'Psychology', 'Random House', 19.99, 'Why habits exist and how to change them.', 10, 10),
('Flow', 'Mihaly Csikszentmihalyi', 'Psychology', 'Harper Perennial', 17.50, 'The psychology of optimal experience.', 7, 7),
('Influence: The Psychology of Persuasion', 'Robert B. Cialdini', 'Psychology', 'Harper Business', 24.00, 'The science of persuasion and influence.', 5, 5),
('Quiet', 'Susan Cain', 'Psychology', 'Crown Publishing', 16.00, 'The power of introverts in a noisy world.', 11, 11),
('Grit', 'Angela Duckworth', 'Self-Help', 'Scribner', 19.00, 'Passion and perseverance for long-term goals.', 9, 9),
('Dare to Lead', 'Brene Brown', 'Leadership', 'Random House', 21.50, 'Brave leadership and courageous communication.', 14, 14),
('Outliers', 'Malcolm Gladwell', 'Psychology', 'Little, Brown and Company', 18.50, 'The story of success and hidden advantages.', 16, 16),
('The 7 Habits of Highly Effective People', 'Stephen R. Covey', 'Self-Help', 'Free Press', 25.00, 'Timeless principles for personal effectiveness.', 30, 30),
('Emotional Intelligence', 'Daniel Goleman', 'Psychology', 'Bantam Books', 22.00, 'Why emotional awareness matters more than IQ.', 12, 12),
('Drive', 'Daniel H. Pink', 'Psychology', 'Riverhead Books', 17.00, 'The surprising truth about motivation.', 8, 8),
('Predictably Irrational', 'Dan Ariely', 'Psychology', 'Harper Perennial', 15.50, 'Hidden forces shaping our decisions.', 10, 10),
('Sapiens', 'Yuval Noah Harari', 'History', 'Harper', 28.00, 'A brief history of humankind.', 25, 25),
('The Subtle Art of Not Giving a F*ck', 'Mark Manson', 'Self-Help', 'HarperOne', 16.99, 'A counterintuitive approach to living well.', 40, 40),
('Blink', 'Malcolm Gladwell', 'Psychology', 'Little, Brown and Company', 17.50, 'The power of thinking without thinking.', 12, 12),
('Start with Why', 'Simon Sinek', 'Leadership', 'Portfolio', 18.99, 'How great leaders inspire action.', 18, 18),
('The Four Agreements', 'Don Miguel Ruiz', 'Self-Help', 'Amber-Allen Publishing', 14.00, 'A practical guide to personal freedom.', 22, 22),
('Awaken the Giant Within', 'Tony Robbins', 'Self-Help', 'Free Press', 20.00, 'Strategies for mastering emotions and finances.', 10, 10),
('Make Your Bed', 'William H. McRaven', 'Self-Help', 'Grand Central Publishing', 13.00, 'Simple habits that can change your life.', 30, 30),
('Can''t Hurt Me', 'David Goggins', 'Self-Help', 'Lioncrest Publishing', 22.99, 'Master your mind and defy the odds.', 15, 15),
('Daring Greatly', 'Brene Brown', 'Self-Help', 'Gotham Books', 17.99, 'The power of vulnerability.', 11, 11),
('Rich Dad Poor Dad', 'Robert T. Kiyosaki', 'Finance', 'Warner Books', 18.00, 'Financial literacy and wealth-building mindset.', 35, 35),

-- Specialized Books
('How to Win Friends and Influence People', 'Dale Carnegie', 'Self-Help', 'Simon & Schuster', 12.99, 'Classic communication and relationship skills.', 15, 15),
('Think and Grow Rich', 'Napoleon Hill', 'Finance', 'The Ralston Society', 10.00, 'The philosophy of personal achievement.', 20, 20),
('The Power of Now', 'Eckhart Tolle', 'Spirituality', 'New World Library', 16.50, 'A guide to spiritual enlightenment and mindfulness.', 12, 12),
('The Courage to Be Disliked', 'Ichiro Kishimi', 'Psychology', 'Allen & Unwin', 18.00, 'Applying Adlerian psychology to daily life.', 10, 10),
('12 Rules for Life', 'Jordan B. Peterson', 'Psychology', 'Penguin Random House', 24.00, 'An antidote to chaos and modern living.', 18, 18),
('The 5 AM Club', 'Robin Sharma', 'Productivity', 'HarperCollins', 19.00, 'How to own your morning and elevate your life.', 25, 25),
('Meditations', 'Marcus Aurelius', 'Philosophy', 'Unknown', 9.99, 'Timeless Stoic wisdom for inner peace.', 30, 30),
('The Body Keeps the Score', 'Bessel van der Kolk', 'Psychology', 'Penguin Books', 22.00, 'Understanding the psychology of trauma.', 15, 15),
('Range', 'David Epstein', 'Self-Help', 'Riverhead Books', 18.50, 'Why generalists triumph in a specialized world.', 12, 12),
('Ikigai', 'Hector Garcia', 'Self-Help', 'Tuttle Publishing', 14.00, 'The Japanese secret to a long and happy life.', 40, 40),
('Digital Minimalism', 'Cal Newport', 'Productivity', 'Portfolio', 20.00, 'Choosing a focused life in a noisy world.', 10, 10),
('The Psychology of Money', 'Morgan Housel', 'Finance', 'Harriman House', 17.50, 'Timeless lessons on wealth and greed.', 35, 35),
('The War of Art', 'Steven Pressfield', 'Self-Help', 'Black Irish Books', 15.00, 'Break through blocks and win creative battles.', 14, 14),
('Big Magic', 'Elizabeth Gilbert', 'Creativity', 'Riverhead Books', 16.00, 'Creative living beyond fear.', 12, 12),
('Limitless', 'Jim Kwik', 'Self-Help', 'Hay House', 21.00, 'Upgrade your brain and learn anything faster.', 20, 20),
('The Art of Learning', 'Josh Waitzkin', 'Self-Help', 'Free Press', 17.00, 'A journey into the pursuit of excellence.', 9, 9),
('Indistractable', 'Nir Eyal', 'Productivity', 'BenBella Books', 19.50, 'How to control your attention and choose your life.', 15, 15),
('Hyperfocus', 'Chris Bailey', 'Productivity', 'Viking', 18.00, 'How to manage your attention in a world of distraction.', 10, 10),
('Show Your Work!', 'Austin Kleon', 'Creativity', 'Workman Publishing', 13.00, '10 ways to share your creativity.', 22, 22),
('Steal Like an Artist', 'Austin Kleon', 'Creativity', 'Workman Publishing', 12.00, 'Things nobody told you about being creative.', 25, 25),
('Talking to Strangers', 'Malcolm Gladwell', 'Psychology', 'Little, Brown and Company', 21.00, 'What we should know about people we don''t know.', 15, 15),
('Originals', 'Adam Grant', 'Psychology', 'Viking', 19.00, 'How non-conformists move the world.', 14, 14),
('Give and Take', 'Adam Grant', 'Psychology', 'Viking', 18.00, 'Why helping others drives our success.', 12, 12),
('Hidden Potential', 'Adam Grant', 'Self-Help', 'Viking', 23.00, 'The science of achieving greater things.', 10, 10),
('The Defining Decade', 'Meg Jay', 'Self-Help', 'Twelve', 16.00, 'Why your twenties matter.', 20, 20),
('Black Box Thinking', 'Matthew Syed', 'Psychology', 'Portfolio', 17.00, 'The surprising truth about success and failure.', 15, 15),
('Bounce', 'Matthew Syed', 'Psychology', 'HarperCollins', 15.50, 'The myth of talent and the power of practice.', 12, 12),
('So Good They Can''t Ignore You', 'Cal Newport', 'Productivity', 'Business Plus', 19.00, 'Why skills trump passion in the quest for work.', 15, 15),
('The Daily Stoic', 'Ryan Holiday', 'Philosophy', 'Portfolio', 20.00, '366 days of Stoic wisdom and reflection.', 25, 25),
('Ego Is the Enemy', 'Ryan Holiday', 'Philosophy', 'Portfolio', 18.00, 'The fight to master our greatest internal opponent.', 18, 18),
('Obstacle Is the Way', 'Ryan Holiday', 'Philosophy', 'Portfolio', 17.50, 'The ancient art of turning adversity to advantage.', 20, 20),
('Stillness Is the Key', 'Ryan Holiday', 'Philosophy', 'Portfolio', 19.00, 'The pathway to self-mastery and focus.', 15, 15),
('Tiny Habits', 'BJ Fogg', 'Self-Help', 'Houghton Mifflin Harcourt', 21.00, 'Small changes that change everything.', 10, 10),
('The Compound Effect', 'Darren Hardy', 'Self-Help', 'Vanguard Press', 16.00, 'Jumpstart your income, your life, your success.', 30, 30),
('Factfulness', 'Hans Rosling', 'Science', 'Flatiron Books', 20.00, 'Ten reasons we''re wrong about the world.', 12, 12),
('Zero to One', 'Peter Thiel', 'Business', 'Crown Business', 22.00, 'Notes on startups and how to build the future.', 15, 15),
('Shoe Dog', 'Phil Knight', 'Business', 'Scribner', 19.00, 'A memoir by the creator of Nike.', 18, 18),
('The Lean Startup', 'Eric Ries', 'Business', 'Crown Business', 24.00, 'How constant innovation creates radical success.', 10, 10),
('Creative Confidence', 'Tom Kelley', 'Creativity', 'Crown Business', 21.50, 'Unleashing the creative potential within us all.', 12, 12),
('Getting Things Done', 'David Allen', 'Productivity', 'Viking', 19.99, 'The art of stress-free productivity.', 20, 20),
('The Comfort Crisis', 'Michael Easter', 'Self-Help', 'Rodale Books', 22.00, 'Embracing discomfort to reclaim our wild self.', 12, 12),
('Four Thousand Weeks', 'Oliver Burkeman', 'Self-Help', 'Farrar, Straus and Giroux', 19.00, 'Time management for mortals.', 14, 14),
('Fooled by Randomness', 'Nassim Taleb', 'Economics', 'Random House', 23.00, 'The hidden role of chance in life and markets.', 8, 8),
('The Black Swan', 'Nassim Taleb', 'Economics', 'Random House', 25.00, 'The impact of the highly improbable.', 10, 10),
('Antifragile', 'Nassim Taleb', 'Economics', 'Random House', 26.00, 'Things that gain from disorder.', 10, 10),
('Never Split the Difference', 'Chris Voss', 'Self-Help', 'Harper Business', 21.00, 'Negotiating as if your life depended on it.', 12, 12),
('Peak', 'Anders Ericsson', 'Self-Help', 'Eamon Dolan/Houghton Mifflin Harcourt', 19.00, 'Secrets from the new science of expertise.', 12, 12),
('The Talent Code', 'Daniel Coyle', 'Self-Help', 'Bantam Books', 18.00, 'Greatness isn''t born. It''s grown.', 15, 15),
('Moonwalking with Einstein', 'Joshua Foer', 'Science', 'Penguin Press', 18.00, 'The art and science of remembering everything.', 12, 12),
('Effortless', 'Greg McKeown', 'Productivity', 'Currency', 20.00, 'Make it easier to do what matters most.', 14, 14),
('The One Thing', 'Gary Keller', 'Productivity', 'Bard Press', 21.00, 'The surprisingly simple truth behind extraordinary results.', 20, 20),
('High Performance Habits', 'Brendon Burchard', 'Self-Help', 'Hay House', 23.00, 'How extraordinary people become that way.', 15, 15),
('Principles', 'Ray Dalio', 'Business', 'Simon & Schuster', 30.00, 'Life and work lessons from a top investor.', 12, 12),
('The Intelligent Investor', 'Benjamin Graham', 'Finance', 'Harper Business', 25.00, 'The definitive book on value investing.', 18, 18),
('Tools of Titans', 'Tim Ferriss', 'Self-Help', 'Houghton Mifflin Harcourt', 28.00, 'The tactics and routines of billionaires and icons.', 15, 15),
('The 4-Hour Workweek', 'Tim Ferriss', 'Self-Help', 'Crown', 20.00, 'Escape 9-5 and live anywhere.', 20, 20);

-- Seed custom ratings and borrow counts for popular/trending books
UPDATE books SET rating = 4.9, borrow_count = 145 WHERE title = 'Atomic Habits';
UPDATE books SET rating = 4.8, borrow_count = 112 WHERE title = 'The Alchemist';
UPDATE books SET rating = 4.7, borrow_count = 89 WHERE title = 'Deep Work';
UPDATE books SET rating = 4.9, borrow_count = 134 WHERE title = 'Rich Dad Poor Dad';
UPDATE books SET rating = 4.8, borrow_count = 110 WHERE title = 'Ikigai';
UPDATE books SET rating = 4.6, borrow_count = 75 WHERE title = 'Thinking, Fast and Slow';
UPDATE books SET rating = 4.7, borrow_count = 64 WHERE title = 'Sapiens';
UPDATE books SET rating = 4.8, borrow_count = 80 WHERE title = 'Meditations';
UPDATE books SET rating = 4.5, borrow_count = 55 WHERE title = '1984';
UPDATE books SET rating = 4.7, borrow_count = 92 WHERE title = 'The Psychology of Money';
UPDATE books SET rating = 4.6, borrow_count = 42 WHERE title = 'Zero to One';
UPDATE books SET rating = 4.8, borrow_count = 78 WHERE title = 'The Daily Stoic';

-- Extended Tables for Book Matrix Settings

-- 1. Detailed User Profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INTEGER PRIMARY KEY,
    account_type TEXT CHECK(account_type IN ('Admin', 'Librarian', 'Teacher', 'Student')) DEFAULT 'Admin',
    avatar_path TEXT DEFAULT 'https://ui-avatars.com/api/?name=Admin+User&background=9d50bb&color=fff',
    avatar_upload_date TEXT,
    avatar_uploaded_by TEXT,
    phone_number TEXT,
    employee_id TEXT UNIQUE,
    student_id TEXT UNIQUE,
    designation TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 2. Library Organization Details
CREATE TABLE IF NOT EXISTS library_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_name TEXT NOT NULL,
    library_code TEXT UNIQUE,
    institution_name TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    zip_code TEXT
);

-- 3. Password Verification & Changes
CREATE TABLE IF NOT EXISTS password_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    password_hash TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Active Device Sessions
CREATE TABLE IF NOT EXISTS user_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    device_type TEXT NOT NULL,
    browser TEXT NOT NULL,
    os TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    last_login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Notification Mapping
CREATE TABLE IF NOT EXISTS user_notifications (
    user_id INTEGER PRIMARY KEY,
    notify_new_member INTEGER DEFAULT 1,
    notify_book_issue INTEGER DEFAULT 1,
    notify_book_return INTEGER DEFAULT 1,
    notify_overdue INTEGER DEFAULT 1,
    notify_fine INTEGER DEFAULT 1,
    notify_new_admin INTEGER DEFAULT 1,
    notify_dashboard INTEGER DEFAULT 1,
    notify_maintenance INTEGER DEFAULT 1,
    notify_database INTEGER DEFAULT 1,
    notify_security INTEGER DEFAULT 1,
    channel_email INTEGER DEFAULT 1,
    channel_sms INTEGER DEFAULT 0,
    channel_in_app INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. Theme and Layout Personalization
CREATE TABLE IF NOT EXISTS theme_settings (
    user_id INTEGER PRIMARY KEY,
    accent_color TEXT CHECK(accent_color IN ('blue', 'purple', 'emerald', 'rose', 'orange')) DEFAULT 'blue',
    visual_mode TEXT CHECK(visual_mode IN ('light', 'dark', 'system')) DEFAULT 'dark',
    glassmorphism INTEGER DEFAULT 1,
    font_family TEXT DEFAULT 'cinzel',
    ui_density TEXT CHECK(ui_density IN ('comfortable', 'compact')) DEFAULT 'comfortable',
    animations_enabled INTEGER DEFAULT 1,
    font_size TEXT DEFAULT '14px',
    font_weight TEXT DEFAULT 'normal',
    letter_spacing TEXT DEFAULT '0px',
    line_height TEXT DEFAULT '1.6',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Audit Logging Registry
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    module TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT NOT NULL,
    device TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Database Backup Logging
CREATE TABLE IF NOT EXISTS backup_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    trigger_type TEXT CHECK(trigger_type IN ('manual', 'auto')) DEFAULT 'manual',
    size_bytes INTEGER NOT NULL,
    duration_ms INTEGER NOT NULL,
    status TEXT CHECK(status IN ('Success', 'Failed')) DEFAULT 'Success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. User Preferences Configuration
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id INTEGER PRIMARY KEY,
    session_timeout INTEGER DEFAULT 30,
    max_login_attempts INTEGER DEFAULT 5,
    lock_duration INTEGER DEFAULT 15,
    auto_logout INTEGER DEFAULT 1,
    email_otp INTEGER DEFAULT 0,
    authenticator_app INTEGER DEFAULT 0,
    backup_schedule TEXT CHECK(backup_schedule IN ('none', 'daily', 'weekly', 'monthly')) DEFAULT 'none',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 10. Login History Registry
CREATE TABLE IF NOT EXISTS login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    ip_address TEXT,
    device_info TEXT,
    status TEXT CHECK(status IN ('Success', 'Failed')) NOT NULL,
    failure_reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. System Notifications Alerts
CREATE TABLE IF NOT EXISTS system_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT CHECK(type IN ('Dashboard', 'Maintenance', 'Database', 'Security')) DEFAULT 'Dashboard',
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert Default Library Settings if none exist
INSERT INTO library_settings (library_name, library_code, institution_name, address, city, state, country, zip_code)
SELECT 'Central Public Library', 'LIB-001', 'City Education Board', '123 Library Avenue', 'New York', 'NY', 'United States', '10001'
WHERE NOT EXISTS (SELECT 1 FROM library_settings);


