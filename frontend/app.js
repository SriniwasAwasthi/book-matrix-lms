// app.js - Main Application Logic for Libraria

// Initialize session token globally
let sessionToken = localStorage.getItem('bookMatrixSessionToken');
if (!sessionToken) {
    sessionToken = 'token_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('bookMatrixSessionToken', sessionToken);
}

// Synchronize user settings, profile sidebar and premium typography
function syncUserProfileAndTheme() {
    // First try to apply settings from LocalStorage immediately for instant render (no flicker)
    try {
        const cachedSettings = localStorage.getItem('bookMatrixSettings');
        if (cachedSettings) {
            const data = JSON.parse(cachedSettings);
            applySharedCustomizations(data);
        }
    } catch (e) {
        console.warn('Error loading cached theme settings', e);
    }

    // Fetch the latest settings from the backend
    fetch(`/api?action=get_settings`, {
        headers: { 'X-Session-Token': sessionToken }
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) return;
        // Save settings to LocalStorage so theme.js can read them on subsequent page loads
        localStorage.setItem('bookMatrixSettings', JSON.stringify(data));
        // Apply customized styles and sidebar details dynamically
        applySharedCustomizations(data);
    })
    .catch(err => console.warn('Could not sync user preferences with server', err));
}

function applySharedCustomizations(data) {
    const root = document.documentElement;

    // Apply accent color
    if (data.customization?.accentColor) {
        const colors = {
            blue: '#00d2ff',
            purple: '#9d50bb',
            emerald: '#00ff87',
            rose: '#ff416c',
            orange: '#ff8c00'
        };
        const activeColor = colors[data.customization.accentColor] || colors.blue;
        root.style.setProperty('--neon-blue', activeColor);
    }

    // Apply font family
    if (data.customization?.fontFamily) {
        const fonts = {
            cinzel: "'Cinzel', serif",
            inter: "'Inter', sans-serif",
            outfit: "'Outfit', sans-serif",
            montserrat: "'Montserrat', sans-serif",
            roboto: "'Roboto', sans-serif"
        };
        const activeFont = fonts[data.customization.fontFamily] || fonts.cinzel;
        root.style.setProperty('--font-body', activeFont);
    }

    // Apply visual mode (dark/light)
    if (data.customization?.visualMode) {
        if (data.customization.visualMode === 'light') {
            root.classList.add('light-mode');
            if (document.body) document.body.classList.add('light-mode');
            // Sync sun/moon icon on the page if present
            const themeToggle = document.getElementById('theme-toggle');
            if (themeToggle) {
                const icon = themeToggle.querySelector('i');
                if (icon) icon.classList.replace('fa-moon', 'fa-sun');
            }
        } else {
            root.classList.remove('light-mode');
            if (document.body) document.body.classList.remove('light-mode');
            // Sync sun/moon icon on the page if present
            const themeToggle = document.getElementById('theme-toggle');
            if (themeToggle) {
                const icon = themeToggle.querySelector('i');
                if (icon) icon.classList.replace('fa-sun', 'fa-moon');
            }
        }
    }

    // Apply glassmorphism
    if (data.customization && data.customization.glassmorphism !== undefined) {
        if (data.customization.glassmorphism === false) {
            root.style.setProperty('--glass-bg', 'rgba(0, 0, 0, 0.3)');
            root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.05)');
        } else {
            root.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.05)');
            root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.1)');
        }
    }

    // Apply typography base styles
    if (data.customization?.fontSize) {
        root.style.setProperty('--font-size-base', data.customization.fontSize);
    }
    if (data.customization?.fontWeight) {
        root.style.setProperty('--font-weight-base', data.customization.fontWeight);
    }
    if (data.customization?.letterSpacing) {
        root.style.setProperty('--letter-spacing-base', data.customization.letterSpacing);
    }
    if (data.customization?.lineHeight) {
        root.style.setProperty('--line-height-base', data.customization.lineHeight);
    }

    // Update Administrator Avatar and Name in the sidebar (runs on all pages!)
    if (data.profile) {
        const sidebarName = document.querySelector('.profile-info h4') || document.getElementById('sidebarAdminName');
        const sidebarAvatar = document.querySelector('.profile-avatar img') || document.getElementById('sidebarAdminAvatar');

        if (sidebarName) {
            sidebarName.textContent = data.profile.fullName || 'Admin User';
        }
        if (sidebarAvatar && data.profile.avatarPath) {
            sidebarAvatar.src = data.profile.avatarPath;
        }
    }
}

function initDashboard() {
    // Fetch Dashboard Stats
    fetch('/api?action=dashboard')
        .then(res => res.json())
        .then(data => {
            if (document.getElementById('total_titles'))
                document.getElementById('total_titles').innerText = data.total_titles !== undefined ? data.total_titles.toLocaleString() : '0';
            if (document.getElementById('total_books'))
                document.getElementById('total_books').innerText = data.total_books !== undefined ? data.total_books.toLocaleString() : '0';
            if (document.getElementById('total_users'))
                document.getElementById('total_users').innerText = data.total_users !== undefined ? data.total_users.toLocaleString() : '0';
            if (document.getElementById('issued_books'))
                document.getElementById('issued_books').innerText = data.issued_books !== undefined ? data.issued_books.toLocaleString() : '0';
        })
        .catch(err => console.error("Error loading dashboard stats:", err));

    // Fetch Popular Books / Recent Books for Dashboard
    fetch('/api?action=get_books')
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById('popular_books_table');
            if (!table) return;

            let html = '';
            // Just take first 4 books as 'popular/recent'
            const popular = data.slice(0, 4);

            if (popular.length === 0) {
                html = '<tr><td colspan="4" style="text-align:center;">No books found</td></tr>';
            } else {
                popular.forEach(b => {
                    const isAvailable = b.avail_qty > 0;
                    const statusClass = isAvailable ? 'status-available' : 'status-borrowed';
                    const statusText = isAvailable ? 'Available' : 'Borrowed';

                    html += `
                        <tr>
                            <td>
                                <div class="book-cell">
                                    <div class="book-cover-mini" style="background: linear-gradient(135deg, var(--neon-blue), var(--neon-purple));"></div>
                                    <div>
                                        <div style="font-weight: 600;">${b.title}</div>
                                        <div style="font-size: 12px; color: var(--text-secondary);">${b.author}</div>
                                    </div>
                                </div>
                            </td>
                            <td><span class="status-badge" style="background: rgba(157, 80, 187, 0.1); color: var(--neon-purple);">${b.category}</span></td>
                            <td>
                                <div style="font-weight: 500;">${b.avail_qty} / ${b.total_qty}</div>
                            </td>
                            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                            <td>
                                <button class="action-btn" title="View" onclick="location.href='book_details.html?id=${b.id}'"><i class="fas fa-external-link-alt"></i></button>
                            </td>
                        </tr>
                    `;
                });
            }
            table.innerHTML = html;
        });

    // Populate Recent Activity Feed with mock data for aesthetic
    const activityFeed = document.getElementById('activity_feed');
    if (activityFeed) {
        // We'll keep the static ones in HTML or populate more here if needed
    }
}

// Members Page Logic
function initMembers() {
    fetch('/api?action=get_users')
        .then(res => res.json())
        .then(data => {
            const tableBody = document.getElementById('members_table_body');
            if (!tableBody) return;

            let html = '';
            data.forEach(u => {
                // Mock roles for variety in UI
                const roles = ['Student', 'Teacher', 'Staff'];
                const role = roles[Math.floor(Math.random() * roles.length)];

                html += `
                    <tr>
                        <td>
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(u.name)}&background=random" style="width: 35px; height: 35px; border-radius: 50%;">
                                <div style="font-weight: 600;">${u.name}</div>
                            </div>
                        </td>
                        <td style="color: var(--text-secondary);">${u.email}</td>
                        <td style="color: var(--text-secondary);">+1 234-567-890</td>
                        <td><span style="padding: 4px 12px; border-radius: 12px; background: rgba(157, 80, 187, 0.1); color: var(--neon-purple); font-size: 12px; font-weight: 600;">${role}</span></td>
                        <td style="color: var(--text-secondary);">May 09, 2026</td>
                        <td><span style="display: flex; align-items: center; gap: 5px; color: var(--success); font-size: 12px; font-weight: 600;"><i class="fas fa-circle" style="font-size: 6px;"></i> Active</span></td>
                        <td>
                            <div style="display: flex; gap: 10px;">
                                <button class="action-btn" style="width: 30px; height: 30px; font-size: 12px;"><i class="fas fa-edit"></i></button>
                                <button class="action-btn" style="width: 30px; height: 30px; font-size: 12px; color: var(--danger);"><i class="fas fa-trash"></i></button>
                            </div>
                        </td>
                    </tr>
                `;
            });
            tableBody.innerHTML = html;
        });
}

// Shared UI Logic
document.addEventListener("DOMContentLoaded", () => {
    // Synchronize settings, profile avatar/name and themes globally
    syncUserProfileAndTheme();

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) icon.classList.replace('fa-moon', 'fa-sun');
        }
    }

    // Active Link Highlighting
    const links = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    links.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('light-mode');
            const isLight = document.body.classList.contains('light-mode');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');

            const icon = themeToggle.querySelector('i');
            if (icon) {
                if (isLight) icon.classList.replace('fa-moon', 'fa-sun');
                else icon.classList.replace('fa-sun', 'fa-moon');
            }
        });
    }

    // Initialize Chat if on messages page
    if (document.getElementById('chat-messages')) {
        initChat();
    }

    // Initialize Notifications Bell Menu
    initNotificationsBell();
});

function initNotificationsBell() {
    const bellBtn = document.querySelector('.header-actions button[title="Notifications"]') || document.querySelector('.action-btn i.fa-bell')?.parentElement;
    if (!bellBtn) return;

    bellBtn.style.position = 'relative';

    let badge = bellBtn.querySelector('.bell-badge');
    if (!badge) {
        badge = document.createElement('span');
        badge.className = 'bell-badge';
        Object.assign(badge.style, {
            position: 'absolute',
            top: '-2px',
            right: '-2px',
            background: '#ff8c00',
            color: 'white',
            borderRadius: '50%',
            width: '16px',
            height: '16px',
            fontSize: '10px',
            fontWeight: 'bold',
            display: 'none',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 8px #ff8c00',
            pointerEvents: 'none'
        });
        bellBtn.appendChild(badge);
    }

    let dropdown = document.getElementById('bellDropdown');
    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.id = 'bellDropdown';
        Object.assign(dropdown.style, {
            position: 'absolute',
            top: '50px',
            right: '0px',
            width: '320px',
            maxHeight: '400px',
            background: 'rgba(25, 25, 35, 0.95)',
            backdropFilter: 'blur(20px)',
            webkitBackdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '12px',
            boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.5)',
            zIndex: '9999',
            display: 'none',
            flexDirection: 'column',
            overflow: 'hidden',
            transition: 'all 0.3s ease'
        });
        
        const parent = bellBtn.parentElement;
        if (parent) {
            parent.style.position = 'relative';
            parent.appendChild(dropdown);
        }
    }

    function fetchNotifications() {
        fetch(`/api?action=get_notifications`, {
            headers: { 'X-Session-Token': sessionToken }
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) return;
            renderBellNotifications(data);
        })
        .catch(err => console.warn('Could not fetch system notifications', err));
    }

    function renderBellNotifications(notifs) {
        const unread = notifs.filter(n => !n.is_read).length;
        if (unread > 0) {
            badge.textContent = unread;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }

        dropdown.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 16px; border-bottom:1px solid rgba(255,255,255,0.08); background: rgba(0,0,0,0.2);">
                <strong style="font-size:13px; color:white;"><i class="fas fa-bell" style="color:var(--neon-blue); margin-right:6px;"></i>System Alerts</strong>
                ${unread > 0 ? `<button id="bellMarkAllRead" style="background:none; border:none; color:var(--neon-blue, #00d2ff); font-size:10px; font-weight:600; cursor:pointer; padding:0; outline:none;">Dismiss All</button>` : ''}
            </div>
            <div class="bell-items-list" style="overflow-y:auto; max-height:300px; display:flex; flex-direction:column;">
                ${notifs.length === 0 ? `
                    <div style="padding:30px 20px; text-align:center; color:var(--text-secondary); font-size:12px;"><i class="fas fa-bell-slash" style="font-size:18px; margin-bottom:8px; display:block; opacity:0.5;"></i>No system alerts found</div>
                ` : notifs.map(n => {
                    const categoryIcons = {
                        'Security': 'fa-shield-alt',
                        'Database': 'fa-database',
                        'Maintenance': 'fa-tools',
                        'Dashboard': 'fa-info-circle'
                    };
                    const colors = {
                        'Security': '#ff416c',
                        'Database': '#00d2ff',
                        'Maintenance': '#ff8c00',
                        'Dashboard': '#00ff87'
                    };
                    const icon = categoryIcons[n.type] || 'fa-bell';
                    const color = colors[n.type] || '#00d2ff';
                    const opacity = n.is_read ? '0.5' : '1';
                    const bg = n.is_read ? 'transparent' : 'rgba(255,255,255,0.02)';
                    
                    return `
                        <div class="bell-item" data-notif-id="${n.id}" style="display:flex; gap:12px; padding:12px 16px; border-bottom:1px solid rgba(255,255,255,0.04); cursor:pointer; background:${bg}; opacity:${opacity}; transition:all 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='${bg}'">
                            <div style="width:30px; height:30px; border-radius:50%; background:${color}15; display:flex; align-items:center; justify-content:center; flex-shrink:0; border: 1px solid ${color}33;">
                                <i class="fas ${icon}" style="color:${color}; font-size:11px;"></i>
                            </div>
                            <div style="flex:1; display:flex; flex-direction:column; gap:2px;">
                                <div style="font-weight:600; font-size:12px; color:white;">${n.title}</div>
                                <div style="font-size:11px; color:var(--text-secondary); line-height:1.4;">${n.message}</div>
                                <div style="font-size:9px; color:rgba(255,255,255,0.3); margin-top:2px; display:flex; align-items:center; gap:4px;"><i class="far fa-clock"></i> ${n.created_at}</div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        dropdown.querySelectorAll('.bell-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = item.dataset.notifId;
                fetch(`/api?action=dismiss_notification`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Session-Token': sessionToken
                    },
                    body: JSON.stringify({ id: parseInt(id) })
                })
                .then(res => res.json())
                .then(resData => {
                    if (resData.success) {
                        fetchNotifications();
                    }
                })
                .catch(() => {
                    item.style.opacity = '0.5';
                    item.style.background = 'transparent';
                });
            });
        });

        const markAllBtn = dropdown.querySelector('#bellMarkAllRead');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const unreadItems = notifs.filter(n => !n.is_read);
                const promises = unreadItems.map(n => 
                    fetch(`/api?action=dismiss_notification`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Session-Token': sessionToken
                        },
                        body: JSON.stringify({ id: n.id })
                    })
                );
                Promise.all(promises)
                    .then(() => fetchNotifications())
                    .catch(() => fetchNotifications());
            });
        }
    }

    bellBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isVisible = dropdown.style.display === 'flex';
        dropdown.style.display = isVisible ? 'none' : 'flex';
        if (!isVisible) {
            fetchNotifications();
        }
    });

    document.addEventListener('click', (e) => {
        if (!bellBtn.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });

    fetchNotifications();
    setInterval(fetchNotifications, 15000);
}

function initChat() {
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const inboxList = document.getElementById('inbox-list');
    const chatHeader = document.getElementById('chat-header');
    const searchConversations = document.getElementById('search-conversations');
    
    // Compose modal elements
    const composeBtn = document.getElementById('compose-btn');
    const composeModal = document.getElementById('compose-modal');
    const closeCompose = document.getElementById('close-compose');
    const cancelCompose = document.getElementById('cancel-compose');
    const startChatBtn = document.getElementById('start-chat');
    const memberSearch = document.getElementById('member-search');
    const memberDropdownList = document.getElementById('member-dropdown-list');
    const memberSelectWrapper = document.getElementById('member-select-wrapper');

    if (!chatMessages || !chatInput || !sendBtn || !inboxList || !chatHeader) return;

    // Chat state
    const chatState = {
        activeContactId: 'assistant',
        contacts: {
            assistant: {
                id: 'assistant',
                name: 'Library Assistant',
                avatar: 'https://ui-avatars.com/api/?name=Library+Assistant&background=00d2ff&color=fff',
                status: 'AI Online',
                lastMessage: 'Ask me anything about books!',
                messages: [
                    { text: "Hello! I am your Library AI. You can ask me to 'list books' or 'search [title]'.", isUser: false }
                ]
            },
            alice: {
                id: 'alice',
                name: 'Alice Smith',
                avatar: 'https://ui-avatars.com/api/?name=Alice+Smith&background=random',
                status: 'Active now',
                lastMessage: 'Is \'Atomic Habits\' available for renewal?',
                messages: [
                    { text: "Hello Admin, I have 'Atomic Habits' and it's due tomorrow. Can I renew it online?", isUser: false },
                    { text: "Hi Alice! Yes, you can renew it. I've updated the return date for you. Enjoy!", isUser: true },
                    { text: "That's great! Thank you so much.", isUser: false }
                ]
            },
            bob: {
                id: 'bob',
                name: 'Bob Jones',
                avatar: 'https://ui-avatars.com/api/?name=Bob+Jones&background=random',
                status: 'Away',
                lastMessage: 'Thank you for the book suggestion!',
                messages: [
                    { text: "Hello Admin! Do you have any suggestions for a good science fiction book?", isUser: false },
                    { text: "Hi Bob! You should definitely check out 'Dune' or 'Project Hail Mary'.", isUser: true },
                    { text: "Thank you for the book suggestion!", isUser: false }
                ]
            },
            system: {
                id: 'system',
                name: 'System Notifications',
                avatar: 'https://ui-avatars.com/api/?name=System&background=ffb800&color=fff',
                status: 'Automated',
                lastMessage: 'Monthly report is ready for review.',
                messages: [
                    { text: "[SYSTEM] Welcome to the System Notifications channel.", isUser: false },
                    { text: "Monthly report is ready for review.", isUser: false }
                ]
            }
        }
    };

    let allMembers = [];
    let selectedMember = null;

    // Fetch members from database for Compose modal
    fetch('/api?action=get_users')
        .then(res => res.json())
        .then(data => {
            allMembers = data;
        })
        .catch(err => console.error("Error fetching users for chat:", err));

    function renderContacts(filterText = '') {
        inboxList.innerHTML = '';
        const contacts = Object.values(chatState.contacts);
        
        contacts.forEach(c => {
            if (filterText && !c.name.toLowerCase().includes(filterText.toLowerCase())) return;

            const item = document.createElement('div');
            item.className = `activity-item ${chatState.activeContactId === c.id ? 'active' : ''}`;
            item.style.padding = '15px';
            item.style.borderRadius = '12px';
            item.style.cursor = 'pointer';
            item.style.marginBottom = '8px';

            let previewText = c.lastMessage || '';
            if (previewText.includes('<')) {
                previewText = previewText.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
            }

            item.innerHTML = `
                <img src="${c.avatar}" class="user-img">
                <div class="activity-desc" style="flex: 1;">
                    <p style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
                        <strong>${c.name}</strong>
                        ${c.id === 'assistant' ? '<span style="font-size:10px; background:rgba(0, 210, 255, 0.15); color:var(--neon-blue); padding:2px 6px; border-radius:10px; font-weight:700;">AI</span>' : ''}
                    </p>
                    <p style="font-size: 12px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px; margin: 0;">${previewText}</p>
                </div>
            `;

            item.addEventListener('click', () => {
                chatState.activeContactId = c.id;
                renderContacts(filterText);
                renderActiveChat();
            });

            inboxList.appendChild(item);
        });
    }

    function renderActiveChat() {
        const activeContact = chatState.contacts[chatState.activeContactId];
        if (!activeContact) return;

        // Render Header
        chatHeader.innerHTML = `
            <div style="display: flex; align-items: center; gap: 15px; width: 100%; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img src="${activeContact.avatar}" style="width: 40px; height: 40px; border-radius: 50%;">
                    <div>
                        <div style="font-weight: 700;">${activeContact.name}</div>
                        <div style="font-size: 12px; color: ${activeContact.status.includes('Online') || activeContact.status.includes('now') ? 'var(--success)' : 'var(--text-secondary)'};">
                            <i class="fas fa-circle" style="font-size: 6px; margin-right: 4px;"></i> ${activeContact.status}
                        </div>
                    </div>
                </div>
                ${activeContact.id !== 'system' ? `
                <div style="display: flex; gap: 12px;">
                    <button class="action-btn" style="width: 36px; height: 36px; border-radius: 50%;"><i class="fas fa-phone"></i></button>
                    <button class="action-btn" style="width: 36px; height: 36px; border-radius: 50%;"><i class="fas fa-video"></i></button>
                </div>
                ` : ''}
            </div>
        `;

        // Render Messages
        chatMessages.innerHTML = '';
        activeContact.messages.forEach(msg => {
            const msgDiv = document.createElement('div');
            msgDiv.style.alignSelf = msg.isUser ? 'flex-end' : 'flex-start';
            msgDiv.style.maxWidth = '70%';
            msgDiv.style.padding = '12px 18px';
            msgDiv.style.background = msg.isUser ? 'var(--neon-blue)' : 'rgba(255,255,255,0.05)';
            msgDiv.style.color = msg.isUser ? 'white' : 'inherit';
            msgDiv.style.borderRadius = msg.isUser ? '18px 18px 2px 18px' : '18px 18px 18px 2px';
            msgDiv.style.fontSize = '14px';
            msgDiv.style.whiteSpace = msg.text.includes('<') ? 'normal' : 'pre-line';
            msgDiv.innerHTML = msg.text;
            chatMessages.appendChild(msgDiv);
        });

        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Configure Input
        if (activeContact.id === 'system') {
            chatInput.disabled = true;
            chatInput.placeholder = "System notifications channel. Replies are disabled.";
            sendBtn.disabled = true;
            sendBtn.style.opacity = '0.5';
        } else {
            chatInput.disabled = false;
            chatInput.placeholder = `Message ${activeContact.name}...`;
            sendBtn.disabled = false;
            sendBtn.style.opacity = '1';
        }
    }

    function showTypingIndicator() {
        let indicator = document.getElementById('typing-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'typing-indicator';
            indicator.className = 'typing-bubble';
            indicator.innerHTML = `
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            `;
            chatMessages.appendChild(indicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    function sendMessage() {
        const activeContact = chatState.contacts[chatState.activeContactId];
        if (!activeContact || activeContact.id === 'system') return;

        const text = chatInput.value.trim();
        if (!text) return;

        // Add user message
        activeContact.messages.push({ text: text, isUser: true });
        activeContact.lastMessage = text;
        chatInput.value = '';

        renderContacts(searchConversations.value);
        renderActiveChat();

        showTypingIndicator();

        // Handle AI or Mock response
        if (activeContact.id === 'assistant') {
            // Talk to backend Library AI or fallback
            getBotResponseGlobal(text, activeContact.messages).then(reply => {
                setTimeout(() => {
                    hideTypingIndicator();
                    activeContact.messages.push({ text: reply, isUser: false });
                    activeContact.lastMessage = reply;
                    renderContacts(searchConversations.value);
                    renderActiveChat();
                }, 600);
            });
        } else {
            // Mock Member response
            setTimeout(() => {
                hideTypingIndicator();
                let mockReply = "Got it! Thanks for the update.";
                if (activeContact.id === 'alice') {
                    if (text.toLowerCase().includes('renew') || text.toLowerCase().includes('date') || text.toLowerCase().includes('ok') || text.toLowerCase().includes('yes')) {
                        mockReply = "Perfect! Thank you so much for extending the return date. Really appreciate your help.";
                    } else {
                        mockReply = "Thanks for the message Admin! I will check that book title next time I visit the library.";
                    }
                } else if (activeContact.id === 'bob') {
                    mockReply = "Awesome. I will drop by the library tomorrow afternoon to borrow it. See you then!";
                } else {
                    mockReply = `Hey Admin, thanks for the message! I've received your update.`;
                }

                activeContact.messages.push({ text: mockReply, isUser: false });
                activeContact.lastMessage = mockReply;
                renderContacts(searchConversations.value);
                renderActiveChat();
            }, 1000);
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    searchConversations.addEventListener('input', (e) => {
        renderContacts(e.target.value);
    });

    // Compose Modal handlers
    composeBtn.addEventListener('click', () => {
        composeModal.classList.add('active');
        memberSearch.value = '';
        selectedMember = null;
        renderComposeDropdown('');
    });

    const closeComposeModal = () => {
        composeModal.classList.remove('active');
        memberDropdownList.style.display = 'none';
        memberSelectWrapper.classList.remove('open');
    };

    closeCompose.addEventListener('click', closeComposeModal);
    cancelCompose.addEventListener('click', closeComposeModal);

    // Search members in compose dropdown
    memberSearch.addEventListener('input', (e) => {
        renderComposeDropdown(e.target.value);
    });

    memberSearch.addEventListener('focus', () => {
        renderComposeDropdown(memberSearch.value);
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!memberSelectWrapper.contains(e.target)) {
            memberDropdownList.style.display = 'none';
            memberSelectWrapper.classList.remove('open');
        }
    });

    function renderComposeDropdown(filterText = '') {
        memberDropdownList.innerHTML = '';
        const filtered = allMembers.filter(m => 
            m.name.toLowerCase().includes(filterText.toLowerCase())
        );

        if (filtered.length === 0) {
            memberDropdownList.innerHTML = '<div class="premium-item" style="color: var(--text-secondary); pointer-events: none;">No members found</div>';
        } else {
            filtered.forEach(m => {
                const item = document.createElement('div');
                item.className = `premium-item ${selectedMember && selectedMember.id === m.id ? 'selected' : ''}`;
                item.innerHTML = `
                    <div class="premium-item-avatar">${m.name.charAt(0).toUpperCase()}</div>
                    <div class="premium-item-content">
                        <span class="premium-item-name">${m.name}</span>
                        <span class="premium-item-sub">${m.email}</span>
                    </div>
                `;
                item.addEventListener('click', () => {
                    selectedMember = m;
                    memberSearch.value = m.name;
                    memberDropdownList.style.display = 'none';
                    memberSelectWrapper.classList.remove('open');
                });
                memberDropdownList.appendChild(item);
            });
        }
        memberDropdownList.style.display = 'block';
        memberSelectWrapper.classList.add('open');
    }

    startChatBtn.addEventListener('click', () => {
        if (!selectedMember) {
            alert('Please select a member first.');
            return;
        }

        const contactId = `user_${selectedMember.id}`;
        if (!chatState.contacts[contactId]) {
            chatState.contacts[contactId] = {
                id: contactId,
                name: selectedMember.name,
                avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(selectedMember.name)}&background=random`,
                status: 'Active now',
                lastMessage: 'No messages yet',
                messages: [
                    { text: `Started a new conversation with ${selectedMember.name}.`, isUser: false }
                ]
            };
        }

        chatState.activeContactId = contactId;
        renderContacts(searchConversations.value);
        renderActiveChat();
        closeComposeModal();
    });

    // Initial render
    renderContacts();
    renderActiveChat();
}

const BOT_IDENTITY = {
    name: "Matrix AI Assistant",
    pronouns: ["Librarian", "Guardian", "Consultant"],
    specialty: "Intellectual Library Management",
    voice: "Analytical & Professional",
    duty: "To search, recommend, and resolve all library-related queries with precision."
};

async function getBotResponseGlobal(input, history = []) {
    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: input, history: history })
        });
        if (res.ok) {
            const data = await res.json();
            if (data && data.reply) {
                return data.reply;
            }
        }
    } catch (e) {
        console.warn("Backend chatbot failed:", e);
    }
    
    return "I'm sorry, I cannot connect to the library database right now. Please try again later.";
}
