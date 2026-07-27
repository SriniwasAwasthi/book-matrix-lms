import os

layout = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Book Matrix | {title}</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="sidebar">
        <div class="logo" style="cursor:pointer" onclick="window.location.href='index.html'">BOOK<br>MATRIX</div>
        <ul class="nav-links">
            <li><a href="index.html" class="{active_index}"><i class="fas fa-chart-pie"></i> Dashboard</a></li>
            <li><a href="books.html" class="{active_books}"><i class="fas fa-book"></i> Books Mgmt</a></li>
            <li><a href="issue_return.html" class="{active_issue}"><i class="fas fa-hand-holding-hand"></i> Issue Book</a></li>
            <li><a href="issue_return.html"><i class="fas fa-undo"></i> Return Book</a></li>
            <li><a href="users.html" class="{active_users}"><i class="fas fa-users"></i> User Mgmt</a></li>
            <li><a href="transactions.html" class="{active_transactions}"><i class="fas fa-list"></i> Transactions</a></li>
        </ul>
        <div class="admin-profile">
            <div class="avatar">AD</div>
            <div class="admin-info">
                <h4>Admin User</h4>
                <p>System Online</p>
            </div>
        </div>
    </div>
    
    <div class="main-content">
        <header>
            <div class="search-bar">
                <i class="fas fa-search"></i>
                <input type="text" placeholder="Search to check if a book is present...">
            </div>
            <div class="header-actions">
                <button class="icon-btn"><i class="fas fa-moon"></i></button>
                <button class="icon-btn"><i class="fas fa-bell"></i></button>
                <a href="issue_return.html" style="text-decoration:none;"><button class="btn-primary"><i class="fas fa-plus"></i> New Issue</button></a>
            </div>
        </header>
        
        {content}
        
    </div>
    <script src="app.js"></script>
</body>
</html>"""

pages = {
    "index.html": {
        "title": "Dashboard",
        "active": "index",
        "content": '''
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(58, 123, 213, 0.1); color: var(--accent-blue);"><i class="fas fa-book"></i></div>
                <div class="stat-info"><h3 id="dash_total">0</h3><p>Total Library Books</p></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(46, 204, 113, 0.1); color: var(--status-returned);"><i class="fas fa-check-circle"></i></div>
                <div class="stat-info"><h3 id="dash_avail">0</h3><p>Available For Issue</p></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(230, 126, 34, 0.1); color: var(--status-issued);"><i class="fas fa-clock"></i></div>
                <div class="stat-info"><h3 id="dash_issued">0</h3><p>Currently Issued</p></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="background: rgba(0, 210, 255, 0.1); color: var(--accent-cyan);"><i class="fas fa-user-friends"></i></div>
                <div class="stat-info"><h3 id="dash_users">0</h3><p>Registered Users</p></div>
            </div>
        </div>
        
        <div class="bottom-grid">
            <div class="panel">
                <div class="panel-header">
                    <h2>Recent Transactions</h2>
                    <a href="transactions.html">View All</a>
                </div>
                <table>
                    <thead><tr><th>Book Title</th><th>Borrowed By</th><th>Issue Date</th><th>Status</th></tr></thead>
                    <tbody id="recent_tx_table"></tbody>
                </table>
            </div>
            <div class="panel">
                <div class="panel-header">
                    <h2>Library Distribution by Category</h2>
                </div>
                <canvas id="categoryChart" style="width:100%; height: 250px;"></canvas>
                <p style="font-size: 11px; color: var(--text-muted); margin-top: 15px; text-align: center;">Shows the total inventory distributed across major study and research categories.</p>
            </div>
        </div>
        '''
    },
    "books.html": {
        "title": "Books Management",
        "active": "books",
        "content": '''
        <div class="bottom-grid">
            <div class="panel" style="grid-column: span 2;">
                <div class="panel-header">
                    <h2>Add New Book</h2>
                </div>
                <div id="msg" class="message" style="display:none; padding:10px; border-radius:5px; margin-bottom:15px;"></div>
                <form id="addBookForm" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div class="form-group"><label>Title</label><input type="text" id="title" required></div>
                    <div class="form-group"><label>Author</label><input type="text" id="author" required></div>
                    <div class="form-group"><label>Price ($)</label><input type="number" step="0.01" id="price" required></div>
                    <div class="form-group"><label>Total Quantity</label><input type="number" id="qty" required></div>
                    <div class="form-group" style="grid-column: span 2;"><label>Description</label><textarea id="description" rows="3"></textarea></div>
                    <div style="grid-column: span 2;"><button type="submit" class="btn-primary">Add Book</button></div>
                </form>
            </div>
            <div class="panel" style="grid-column: span 2;">
                <div class="panel-header">
                    <h2>Book Catalog</h2>
                </div>
                <table>
                    <thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Price</th><th>Total Qty</th><th>Avail Qty</th></tr></thead>
                    <tbody id="booksTable"></tbody>
                </table>
            </div>
        </div>
        '''
    },
    "users.html": {
        "title": "User Management",
        "active": "users",
        "content": '''
        <div class="bottom-grid">
            <div class="panel">
                <div class="panel-header"><h2>Add New User</h2></div>
                <div id="msg" class="message" style="display:none; padding:10px; border-radius:5px; margin-bottom:15px;"></div>
                <form id="addUserForm">
                    <div class="form-group"><label>Full Name</label><input type="text" id="name" required></div>
                    <div class="form-group"><label>Email Address</label><input type="email" id="email" required></div>
                    <button type="submit" class="btn-primary">Add User</button>
                </form>
            </div>
            <div class="panel">
                <div class="panel-header"><h2>Registered Users</h2></div>
                <table>
                    <thead><tr><th>ID</th><th>Name</th><th>Email</th></tr></thead>
                    <tbody id="usersTable"></tbody>
                </table>
            </div>
        </div>
        '''
    },
    "issue_return.html": {
        "title": "Issue / Return Book",
        "active": "issue",
        "content": '''
        <div class="bottom-grid">
            <div class="panel">
                <div class="panel-header"><h2>Issue Book</h2></div>
                <div id="msgIssue" class="message" style="display:none; padding:10px; border-radius:5px; margin-bottom:15px;"></div>
                <form id="issueForm">
                    <div class="form-group"><label>Select User</label><select id="userSelect" required></select></div>
                    <div class="form-group"><label>Select Book</label><select id="bookSelect" required></select></div>
                    <div class="form-group"><label>Expected Return Date</label><input type="date" id="returnDate" required></div>
                    <button type="submit" class="btn-primary">Issue Book</button>
                </form>
            </div>
            <div class="panel">
                <div class="panel-header"><h2>Return Book</h2></div>
                <div id="msgReturn" class="message" style="display:none; padding:10px; border-radius:5px; margin-bottom:15px;"></div>
                <form id="returnForm">
                    <div class="form-group"><label>Transaction ID</label><input type="number" id="transactionId" placeholder="Enter Transaction ID" required></div>
                    <button type="submit" class="btn-primary" style="background: var(--status-returned); box-shadow: 0 4px 15px rgba(46,204,113,0.3);">Return Book</button>
                </form>
            </div>
        </div>
        '''
    },
    "transactions.html": {
        "title": "Transactions",
        "active": "transactions",
        "content": '''
        <div class="panel">
            <div class="panel-header"><h2>All Transactions</h2></div>
            <table>
                <thead><tr><th>Tx ID</th><th>User</th><th>Book</th><th>Issue Date</th><th>Exp. Return</th><th>Actual Return</th><th>Status</th></tr></thead>
                <tbody id="txTable"></tbody>
            </table>
        </div>
        '''
    }
}

for filename, data in pages.items():
    html = layout.format(
        title=data['title'],
        active_index='active' if data['active'] == 'index' else '',
        active_books='active' if data['active'] == 'books' else '',
        active_issue='active' if data['active'] == 'issue' else '',
        active_users='active' if data['active'] == 'users' else '',
        active_transactions='active' if data['active'] == 'transactions' else '',
        content=data['content']
    )
    with open(f"frontend/{filename}", "w", encoding='utf-8') as f:
        f.write(html)
