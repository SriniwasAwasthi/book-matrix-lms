(function () {
    'use strict';

    const STORAGE_KEY = 'bookMatrixSettings';
    const AVATAR_KEY = 'bookMatrixAvatar';
    const PAGE_SIZE = 5;

    let hasUnsavedChanges = false;
    let pendingTab = null;
    let restoreFile = null;
    let avatarDataUrl = null;

    // Cropping variables
    let cropperImage = null;
    let cropZoom = 1.0;
    let cropRotation = 0;
    let isDragging = false;
    let startX = 0;
    let startY = 0;
    let imgX = 0;
    let imgY = 0;

    // Generate unique session token for active browser session if none exists
    let sessionToken = localStorage.getItem('bookMatrixSessionToken');
    if (!sessionToken) {
        sessionToken = 'token_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
        localStorage.setItem('bookMatrixSessionToken', sessionToken);
    }

    const auditLogsFallback = [
        { timestamp: 'May 31, 2026 - 10:45 AM', user: 'Admin User', action: 'Database Backup', module: 'Database', ip: '192.168.1.100', status: 'Success' },
        { timestamp: 'May 31, 2026 - 09:30 AM', user: 'Admin User', action: 'Book Added', module: 'Books', ip: '192.168.1.100', status: 'Success' },
        { timestamp: 'May 31, 2026 - 08:15 AM', user: 'Admin User', action: 'User Registered', module: 'Members', ip: '192.168.1.100', status: 'Success' },
        { timestamp: 'May 30, 2026 - 11:20 PM', user: 'System', action: 'Scheduled Backup', module: 'Database', ip: '127.0.0.1', status: 'Success' },
        { timestamp: 'May 30, 2026 - 02:30 PM', user: 'Admin User', action: 'Database Optimized', module: 'Database', ip: '192.168.1.100', status: 'Success' },
        { timestamp: 'May 30, 2026 - 09:00 AM', user: 'Admin User', action: 'Failed Login Attempt', module: 'Security', ip: '203.0.113.42', status: 'Failed' }
    ];

    let auditPage = 1;
    let auditLoaded = false;

    const validators = {
        email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
        phone: (v) => !v || /^[+]?[\d\s().-]{7,20}$/.test(v.trim()),
        required: (v) => v.trim().length > 0
    };

    function $(id) {
        return document.getElementById(id);
    }

    // Custom API Fetch Wrapper injecting Session headers
    function apiFetch(url, options = {}) {
        options.headers = options.headers || {};
        options.headers['X-Session-Token'] = sessionToken;
        return fetch(url, options);
    }

    function showToast(message, type = 'success') {
        const container = $('toastContainer');
        if (!container) {
            // Create container if missing
            const div = document.createElement('div');
            div.id = 'toastContainer';
            div.className = 'settings-toast-container';
            document.body.appendChild(div);
        }
        const activeContainer = $('toastContainer');
        const toast = document.createElement('div');
        toast.className = `settings-toast ${type}`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}" aria-hidden="true"></i> ${message}`;
        activeContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(120%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3200);
    }

    function markDirty() {
        hasUnsavedChanges = true;
        const saveBtn = $('saveSettingsBtn');
        if (saveBtn) {
            saveBtn.classList.add('has-changes');
            saveBtn.setAttribute('aria-label', 'Save changes — unsaved modifications pending');
        }
    }

    function markClean() {
        hasUnsavedChanges = false;
        const saveBtn = $('saveSettingsBtn');
        if (saveBtn) {
            saveBtn.classList.remove('has-changes');
            saveBtn.setAttribute('aria-label', 'Save changes');
        }
    }

    function openModal(id) {
        const modal = $(id);
        if (modal) {
            modal.classList.add('active');
            modal.setAttribute('aria-hidden', 'false');
        }
    }

    function closeModal(id) {
        const modal = $(id);
        if (modal) {
            modal.classList.remove('active');
            modal.setAttribute('aria-hidden', 'true');
        }
    }

    function openTab(tabName) {
        document.querySelectorAll('.settings-content').forEach((el) => {
            el.classList.remove('active');
            el.hidden = true;
        });
        document.querySelectorAll('.settings-menu-item').forEach((el) => {
            el.classList.remove('active');
            el.setAttribute('aria-selected', 'false');
        });

        const panel = $(tabName);
        const menuItem = document.querySelector(`.settings-menu-item[data-tab="${tabName}"]`);
        if (panel) {
            panel.classList.add('active');
            panel.hidden = false;
        }
        if (menuItem) {
            menuItem.classList.add('active');
            menuItem.setAttribute('aria-selected', 'true');
        }

        if (tabName === 'database' && !auditLoaded) {
            renderAuditLogs();
            auditLoaded = true;
        }
        if (tabName === 'database') {
            fetchDatabaseStats();
            fetchDevices();
            fetchBackups();
        }
    }

    function trySwitchTab(tabName) {
        if (hasUnsavedChanges) {
            pendingTab = tabName;
            openModal('unsavedModal');
            return;
        }
        openTab(tabName);
    }

    function collectSettings() {
        return {
            profile: {
                fullName: $('fullName')?.value || '',
                username: $('username')?.value || '',
                email: $('email')?.value || '',
                phone: $('phone')?.value || '',
                designation: $('designation')?.value || '',
                accountType: $('accountType')?.value || 'Admin',
                employeeId: $('employeeId')?.value || '',
                studentId: $('studentId')?.value || ''
            },
            library: {
                libraryName: $('libraryName')?.value || '',
                libraryCode: $('libraryCode')?.value || '',
                institutionName: $('institutionName')?.value || '',
                address: $('address')?.value || '',
                city: $('city')?.value || '',
                state: $('state')?.value || '',
                country: $('country')?.value || '',
                zipCode: $('zipCode')?.value || ''
            },
            security: {
                sessionTimeout: $('sessionTimeout')?.value || '30',
                maxLoginAttempts: $('maxLoginAttempts')?.value || '5',
                lockDuration: $('lockDuration')?.value || '15',
                autoLogout: $('autoLogout')?.checked ?? true,
                emailOtp: $('emailOtp')?.checked ?? false,
                authenticatorApp: $('authenticatorApp')?.checked ?? false
            },
            notifications: getNotificationState(),
            backupSchedule: $('backupSchedule')?.value || 'none',
            customization: {
                accentColor: document.querySelector('.color-dot.active')?.dataset.color || 'blue',
                glassmorphism: $('glassmorphism')?.checked ?? true,
                fontFamily: $('fontFamily')?.value || 'cinzel',
                uiDensity: $('uiDensity')?.value || 'comfortable',
                animationsEnabled: $('animationsEnabled')?.checked ?? true,
                fontSize: $('fontSize')?.value || '14px',
                fontWeight: $('fontWeight')?.value || 'normal',
                letterSpacing: $('letterSpacing')?.value || '0px',
                lineHeight: $('lineHeight')?.value || '1.6',
                visualMode: $('visualMode')?.value || 'dark'
            }
        };
    }

    function getNotificationState() {
        const toggles = {};
        document.querySelectorAll('[data-notify]').forEach((el) => {
            toggles[el.dataset.notify] = el.checked;
        });
        return {
            toggles,
            channels: {
                email: $('channelEmail')?.checked ?? false,
                sms: $('channelSms')?.checked ?? false,
                inApp: $('channelInApp')?.checked ?? false
            }
        };
    }

    function applySettings(data) {
        if (!data) return;
        const set = (id, val) => { const el = $(id); if (el && val !== undefined) el.value = val; };
        const setCheck = (id, val) => { const el = $(id); if (el && val !== undefined) el.checked = val; };

        if (data.profile) {
            set('fullName', data.profile.fullName);
            set('username', data.profile.username);
            set('email', data.profile.email);
            set('phone', data.profile.phone);
            set('designation', data.profile.designation);
            set('accountType', data.profile.accountType);
            set('employeeId', data.profile.employeeId);
            set('studentId', data.profile.studentId);
        }
        if (data.library) {
            Object.entries(data.library).forEach(([key, val]) => {
                const map = { libraryName: 'libraryName', libraryCode: 'libraryCode', institutionName: 'institutionName', address: 'address', city: 'city', state: 'state', country: 'country', zipCode: 'zipCode' };
                set(map[key] || key, val);
            });
        }
        if (data.security) {
            set('sessionTimeout', data.security.sessionTimeout);
            set('maxLoginAttempts', data.security.maxLoginAttempts);
            set('lockDuration', data.security.lockDuration);
            setCheck('autoLogout', data.security.autoLogout);
            setCheck('emailOtp', data.security.emailOtp);
            setCheck('authenticatorApp', data.security.authenticatorApp);
        }
        if (data.notifications?.toggles) {
            Object.entries(data.notifications.toggles).forEach(([key, val]) => {
                const el = document.querySelector(`[data-notify="${key}"]`);
                if (el) el.checked = val;
            });
        }
        if (data.notifications?.channels) {
            setCheck('channelEmail', data.notifications.channels.email);
            setCheck('channelSms', data.notifications.channels.sms);
            setCheck('channelInApp', data.notifications.channels.inApp);
        }
        if (data.backupSchedule) set('backupSchedule', data.backupSchedule);

        if (data.customization) {
            setCheck('glassmorphism', data.customization.glassmorphism);
            set('fontFamily', data.customization.fontFamily);
            set('uiDensity', data.customization.uiDensity);
            setCheck('animationsEnabled', data.customization.animationsEnabled);
            set('fontSize', data.customization.fontSize || '14px');
            set('fontWeight', data.customization.fontWeight || 'normal');
            set('letterSpacing', data.customization.letterSpacing || '0px');
            set('lineHeight', data.customization.lineHeight || '1.6');
            set('visualMode', data.customization.visualMode || 'dark');
            
            const color = data.customization.accentColor || 'blue';
            document.querySelectorAll('.color-dot').forEach((btn) => {
                const isActive = btn.dataset.color === color;
                btn.classList.toggle('active', isActive);
                btn.style.borderColor = isActive ? 'white' : 'transparent';
            });
            updatePreviewUI();
        }

        updateProfileDisplay(data.profile?.fullName || 'Admin User');
        toggleIdFields();
    }

    function updatePreviewUI() {
        const family = $('fontFamily')?.value || 'cinzel';
        const density = $('uiDensity')?.value || 'comfortable';
        const color = document.querySelector('.color-dot.active')?.dataset.color || 'blue';
        const glass = $('glassmorphism')?.checked ?? true;
        const size = $('fontSize')?.value || '14px';
        const weight = $('fontWeight')?.value || '400';
        const spacing = $('letterSpacing')?.value || '0px';
        const height = $('lineHeight')?.value || '1.6';
        const mode = $('visualMode')?.value || 'dark';

        const card = $('uiPreviewCard');
        const heading = $('previewHeading');
        const badge = $('previewBadge');

        if (!card) return;

        const fonts = {
            cinzel: "'Cinzel', serif",
            inter: "'Inter', sans-serif",
            outfit: "'Outfit', sans-serif",
            montserrat: "'Montserrat', sans-serif",
            roboto: "'Roboto', sans-serif"
        };
        card.style.fontFamily = fonts[family] || fonts.cinzel;
        card.style.fontSize = size;
        card.style.fontWeight = weight;
        card.style.letterSpacing = spacing;
        card.style.lineHeight = height;

        if (heading) heading.style.fontFamily = fonts[family] || fonts.cinzel;

        const colors = {
            blue: '#00d2ff',
            purple: '#9d50bb',
            emerald: '#00ff87',
            rose: '#ff416c',
            orange: '#ff8c00'
        };
        const activeColor = colors[color] || colors.blue;
        if (heading) heading.style.color = activeColor;
        if (badge) {
            badge.style.color = activeColor;
            badge.style.background = `${activeColor}22`;
            badge.textContent = `${color.charAt(0).toUpperCase() + color.slice(1)} Mode`;
        }

        if (density === 'compact') {
            card.style.padding = '10px 16px';
        } else {
            card.style.padding = '20px';
        }

        if (mode === 'light') {
            card.style.color = '#0f172a';
            if (glass) {
                card.style.background = 'rgba(255, 255, 255, 0.7)';
                card.style.border = '1px solid rgba(0, 0, 0, 0.08)';
            } else {
                card.style.background = '#f8fafc';
                card.style.border = '1px solid rgba(0, 0, 0, 0.1)';
            }
        } else {
            card.style.color = '#ffffff';
            if (glass) {
                card.style.background = 'rgba(255, 255, 255, 0.05)';
                card.style.border = '1px solid rgba(255, 255, 255, 0.1)';
            } else {
                card.style.background = 'rgba(0, 0, 0, 0.3)';
                card.style.border = '1px solid rgba(255, 255, 255, 0.05)';
            }
        }
    }

    function loadSettings() {
        apiFetch('/api?action=get_settings')
            .then((res) => res.json())
            .then((data) => {
                if (data.error) {
                    loadSettingsFromLocalStorage();
                    return;
                }
                applySettings(data);
                
                // Cache settings immediately in LocalStorage to synchronize layout/theme across pages
                localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
                
                if (data.profile?.avatarPath) {
                    avatarDataUrl = data.profile.avatarPath;
                    setAvatarPreview(avatarDataUrl);
                    localStorage.setItem(AVATAR_KEY, avatarDataUrl);
                }
                toggleIdFields();
            })
            .catch((err) => {
                console.warn('Could not connect to backend, falling back to local settings.', err);
                loadSettingsFromLocalStorage();
            });
    }

    function loadSettingsFromLocalStorage() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) applySettings(JSON.parse(saved));
        } catch (e) {
            console.warn('Could not load saved settings from local storage', e);
        }

        const avatar = localStorage.getItem(AVATAR_KEY);
        if (avatar) {
            avatarDataUrl = avatar;
            setAvatarPreview(avatar);
        }
        toggleIdFields();
    }

    function toggleIdFields() {
        const type = $('accountType')?.value || 'Admin';
        const empGroup = $('employeeIdGroup');
        const stdGroup = $('studentIdGroup');
        if (type === 'Admin' || type === 'Librarian' || type === 'Teacher') {
            if (empGroup) empGroup.style.display = 'block';
            if (stdGroup) stdGroup.style.display = 'none';
        } else {
            if (empGroup) empGroup.style.display = 'none';
            if (stdGroup) stdGroup.style.display = 'block';
        }
    }

    function validateProfileForm() {
        let valid = true;
        const type = $('accountType')?.value || 'Admin';
        const fields = [
            { id: 'fullName', type: 'required', message: 'Full name is required' },
            { id: 'username', type: 'required', message: 'Username is required' },
            { id: 'email', type: 'email', message: 'Enter a valid email address' },
            { id: 'phone', type: 'phone', message: 'Enter a valid phone number' },
            { id: 'libraryName', type: 'required', message: 'Library name is required' },
            { id: 'institutionName', type: 'required', message: 'Institution name is required' },
            { id: 'address', type: 'required', message: 'Address is required' },
            { id: 'city', type: 'required', message: 'City is required' },
            { id: 'state', type: 'required', message: 'State is required' },
            { id: 'country', type: 'required', message: 'Country is required' }
        ];

        if (type === 'Admin' || type === 'Librarian' || type === 'Teacher') {
            fields.push({ id: 'employeeId', type: 'required', message: 'Employee ID is required' });
        } else {
            fields.push({ id: 'studentId', type: 'required', message: 'Student ID is required' });
        }

        fields.forEach(({ id, type, message }) => {
            const input = $(id);
            const errorEl = $(`${id}Error`);
            if (!input) return;

            let ok = true;
            if (type === 'required') ok = validators.required(input.value);
            else if (type === 'email') ok = validators.required(input.value) && validators.email(input.value);
            else if (type === 'phone') ok = validators.phone(input.value);

            input.classList.toggle('invalid', !ok);
            input.classList.toggle('valid', ok && input.value.trim());
            if (errorEl) errorEl.textContent = ok ? '' : message;
            if (!ok) valid = false;
        });

        return valid;
    }

    function validateField(input, type, message, errorId) {
        let ok = true;
        if (type === 'required') ok = validators.required(input.value);
        else if (type === 'email') ok = validators.required(input.value) && validators.email(input.value);
        else if (type === 'phone') ok = validators.phone(input.value);

        input.classList.toggle('invalid', !ok);
        input.classList.toggle('valid', ok && input.value.trim());
        const errorEl = $(errorId);
        if (errorEl) errorEl.textContent = ok ? '' : message;
        return ok;
    }

    function saveSettings() {
        if (!validateProfileForm()) {
            showToast('Please fix validation errors before saving', 'error');
            openTab('profile');
            return;
        }

        const data = collectSettings();
        
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        if (avatarDataUrl) {
            localStorage.setItem(AVATAR_KEY, avatarDataUrl);
        } else {
            localStorage.removeItem(AVATAR_KEY);
        }

        // Post settings updates to backend
        const profilePayload = {
            profile: data.profile,
            library: data.library,
            security: data.security,
            backupSchedule: data.backupSchedule
        };
        
        apiFetch('/api?action=update_profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profilePayload)
        })
        .then(res => res.json())
        .then(resData => {
            if (resData.error) throw new Error(resData.error);
            
            return apiFetch('/api?action=update_notifications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data.notifications)
            });
        })
        .then(res => res.json())
        .then(resData => {
            if (resData.error) throw new Error(resData.error);
            
            return apiFetch('/api?action=update_theme', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ customization: data.customization })
            });
        })
        .then(res => res.json())
        .then(resData => {
            if (resData.error) throw new Error(resData.error);
            
            // Apply customization properties dynamically and instantly
            const root = document.documentElement;
            const colors = {
                blue: '#00d2ff',
                purple: '#9d50bb',
                emerald: '#00ff87',
                rose: '#ff416c',
                orange: '#ff8c00'
            };
            const activeColor = colors[data.customization.accentColor] || colors.blue;
            root.style.setProperty('--neon-blue', activeColor);
            
            const fonts = {
                cinzel: "'Cinzel', serif",
                inter: "'Inter', sans-serif",
                outfit: "'Outfit', sans-serif",
                montserrat: "'Montserrat', sans-serif",
                roboto: "'Roboto', sans-serif"
            };
            const activeFont = fonts[data.customization.fontFamily] || fonts.cinzel;
            root.style.setProperty('--font-body', activeFont);
            
            if (data.customization.visualMode === 'light') {
                root.classList.add('light-mode');
            } else {
                root.classList.remove('light-mode');
            }
            
            if (data.customization.glassmorphism === false) {
                root.style.setProperty('--glass-bg', 'rgba(0, 0, 0, 0.3)');
                root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.05)');
            } else {
                root.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.05)');
                root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.1)');
            }
            
            root.style.setProperty('--font-size-base', data.customization.fontSize || '14px');
            root.style.setProperty('--font-weight-base', data.customization.fontWeight || '400');
            root.style.setProperty('--letter-spacing-base', data.customization.letterSpacing || '0px');
            root.style.setProperty('--line-height-base', data.customization.lineHeight || '1.6');
            
            updateProfileDisplay(data.profile.fullName);
            markClean();
            showToast('All changes synchronized with server successfully');
        })
        .catch(err => {
            console.error('Failed to sync settings with server', err);
            updateProfileDisplay(data.profile.fullName);
            markClean();
            showToast('Changes saved locally (Offline mode)');
        });
    }

    function updateProfileDisplay(name) {
        const sidebarName = $('sidebarAdminName');
        const sidebarAvatar = $('sidebarAdminAvatar');
        if (sidebarName) sidebarName.textContent = name || 'Admin User';

        const avatarSrc = avatarDataUrl || `https://ui-avatars.com/api/?name=${encodeURIComponent(name || 'Admin')}&background=9d50bb&color=fff`;
        if (sidebarAvatar) sidebarAvatar.src = avatarSrc;
    }

    function setAvatarPreview(src) {
        const display = $('avatarDisplay');
        if (display) display.innerHTML = `<img src="${src}" alt="Administrator profile photo" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
    }

    function drawCropCanvas() {
        const canvas = $('cropCanvas');
        if (!canvas || !cropperImage) return;
        const ctx = canvas.getContext('2d');
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.save();
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.translate(imgX, imgY);
        ctx.rotate((cropRotation * Math.PI) / 180);
        ctx.scale(cropZoom, cropZoom);
        
        const scale = Math.max(300 / cropperImage.width, 300 / cropperImage.height);
        const dw = cropperImage.width * scale;
        const dh = cropperImage.height * scale;
        
        ctx.drawImage(cropperImage, -dw / 2, -dh / 2, dw, dh);
        ctx.restore();
    }

    function saveCrop() {
        const canvas = $('cropCanvas');
        if (!canvas) return;

        const exportCanvas = document.createElement('canvas');
        exportCanvas.width = 200;
        exportCanvas.height = 200;
        const exportCtx = exportCanvas.getContext('2d');
        exportCtx.drawImage(canvas, 50, 50, 200, 200, 0, 0, 200, 200);

        const croppedBase64 = exportCanvas.toDataURL('image/png');
        setAvatarPreview(croppedBase64);

        apiFetch('/api?action=upload_avatar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ avatar_data: croppedBase64, filename: 'avatar.png' })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
            } else {
                avatarDataUrl = data.avatar_path;
                setAvatarPreview(avatarDataUrl);
                updateProfileDisplay($('fullName')?.value || 'Admin User');
                showToast('Avatar cropped and uploaded successfully!');
                closeModal('cropperModal');
            }
        })
        .catch(() => {
            avatarDataUrl = croppedBase64;
            markDirty();
            showToast('Avatar updated locally — save to apply offline');
            closeModal('cropperModal');
        });
    }

    function previewAvatar(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (file.size > 2 * 1024 * 1024) {
            showToast('File size exceeds 2MB limit', 'error');
            event.target.value = '';
            return;
        }
        if (!['image/png', 'image/jpeg', 'image/jpg', 'image/webp'].includes(file.type)) {
            showToast('Only PNG, JPG, and WEBP files are supported', 'error');
            event.target.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const rawBase64 = e.target.result;
            cropperImage = new Image();
            cropperImage.onload = () => {
                const canvas = $('cropCanvas');
                if (canvas) {
                    canvas.width = 300;
                    canvas.height = 300;
                }
                cropZoom = 1.0;
                cropRotation = 0;
                imgX = 0;
                imgY = 0;
                if ($('cropZoomSlider')) $('cropZoomSlider').value = 1.0;
                
                drawCropCanvas();
                openModal('cropperModal');
            };
            cropperImage.src = rawBase64;
        };
        reader.readAsDataURL(file);
    }

    function removeAvatar() {
        apiFetch('/api?action=remove_avatar', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            avatarDataUrl = data.avatar_path;
            $('avatarInput').value = '';
            setAvatarPreview(avatarDataUrl);
            updateProfileDisplay($('fullName')?.value || 'Admin User');
            showToast('Avatar removed successfully');
        })
        .catch(() => {
            avatarDataUrl = null;
            $('avatarInput').value = '';
            $('avatarDisplay').innerHTML = '<i class="fas fa-user" aria-hidden="true"></i>';
            updateProfileDisplay($('fullName')?.value || 'Admin User');
            markDirty();
            showToast('Avatar removed offline — save to apply');
        });
    }

    function togglePasswordVisibility(fieldId, btn) {
        const field = $(fieldId);
        if (!field) return;
        const hidden = field.type === 'password';
        field.type = hidden ? 'text' : 'password';
        btn.setAttribute('aria-label', hidden ? 'Hide password' : 'Show password');
        btn.querySelector('i').className = hidden ? 'fas fa-eye-slash' : 'fas fa-eye';
    }

    function checkPasswordStrength() {
        const password = $('newPassword')?.value || '';
        const bar = $('strengthBar');
        const text = $('strengthText');
        if (!bar || !text) return;

        if (!password) {
            bar.className = 'settings-strength-bar';
            text.textContent = 'Enter a password';
            return;
        }

        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[!@#$%^&*()_+-=[]{}|;:,.<>?~`]/.test(password)) strength++;

        bar.className = 'settings-strength-bar';
        if (strength < 2) {
            bar.classList.add('weak');
            text.textContent = 'Weak password';
        } else if (strength < 4) {
            bar.classList.add('medium');
            text.textContent = 'Medium strength';
        } else {
            bar.classList.add('strong');
            text.textContent = 'Strong password';
        }
        validatePasswordMatch();
    }

    function validatePasswordMatch() {
        const newPass = $('newPassword')?.value || '';
        const confirm = $('confirmPassword')?.value || '';
        const errorEl = $('confirmPasswordError');
        if (!confirm) {
            if (errorEl) errorEl.textContent = '';
            return true;
        }
        const match = newPass === confirm;
        if (errorEl) errorEl.textContent = match ? '' : 'Passwords do not match';
        $('confirmPassword')?.classList.toggle('invalid', !match);
        $('confirmPassword')?.classList.toggle('valid', match);
        return match;
    }

    function changePassword() {
        const current = $('currentPassword')?.value || '';
        const newPass = $('newPassword')?.value || '';
        const confirm = $('confirmPassword')?.value || '';

        if (!current || !newPass || !confirm) {
            showToast('Please fill all password fields', 'error');
            return;
        }
        if (!validatePasswordMatch()) {
            showToast('Passwords do not match', 'error');
            return;
        }
        if (newPass.length < 8) {
            showToast('Password must be at least 8 characters', 'error');
            return;
        }

        apiFetch('/api?action=update_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ currentPassword: current, newPassword: newPass })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
            } else {
                $('currentPassword').value = '';
                $('newPassword').value = '';
                $('confirmPassword').value = '';
                checkPasswordStrength();
                showToast('Password changed successfully');
            }
        })
        .catch(err => {
            showToast('Failed to change password: Server is offline', 'error');
        });
    }

    function generateRecoveryCodes() {
        const codes = Array.from({ length: 8 }, () => Math.random().toString(36).slice(2, 10).toUpperCase());
        $('recoveryCodesList').textContent = codes.join('\n');
        openModal('recoveryCodesModal');
        showToast('Recovery codes generated');
    }

    function fetchDevices() {
        apiFetch('/api?action=get_devices')
            .then(res => res.json())
            .then(data => {
                if (data.error) return;
                renderDevicesUI(data);
            })
            .catch(() => {});
    }
    
    function renderDevicesUI(devices) {
        const tbody = document.querySelector('.settings-table tbody');
        if (!tbody) return;
        
        if (!devices || devices.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);">No active sessions found</td></tr>`;
            return;
        }
        
        tbody.innerHTML = devices.map(dev => {
            const isCurrent = dev.session_token === sessionToken;
            const currentBadge = isCurrent ? '<span class="settings-badge" style="margin-left:8px;">Current</span>' : '';
            const statusClass = dev.is_active ? 'settings-session-current' : '';
            const logoutButton = isCurrent ? 
                `<button type="button" class="settings-btn settings-btn-danger" disabled title="Cannot logout current session from here"><i class="fas fa-ban"></i> Terminate</button>` :
                `<button type="button" class="settings-btn settings-btn-danger" onclick="logoutDevice('${dev.session_token}')"><i class="fas fa-sign-out-alt"></i> Logout</button>`;
                
            const icon = dev.device_type === 'Mobile' ? 'fa-mobile-alt' : 'fa-laptop';
            
            return `<tr class="${statusClass}" data-session-id="${dev.session_token}" ${isCurrent ? 'data-current="true"' : ''}>
                <td><i class="fas ${icon}"></i> ${dev.device_type} ${currentBadge}</td>
                <td>${dev.browser}</td>
                <td>${dev.os}</td>
                <td>${dev.ip_address}</td>
                <td>${logoutButton}</td>
            </tr>`;
        }).join('');
    }

    function logoutDevice(id) {
        apiFetch('/api?action=logout_device', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_token: id })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            showToast('Device session logged out');
            fetchDevices();
        })
        .catch(() => {
            const row = document.querySelector(`[data-session-id="${id}"]`);
            if (row) row.remove();
            showToast('Device session logged out (Offline)');
        });
    }

    function logoutAllDevices() {
        apiFetch('/api?action=logout_all_devices', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            showToast('All other devices logged out');
            fetchDevices();
        })
        .catch(() => {
            document.querySelectorAll('[data-session-id]:not([data-current="true"])').forEach((row) => row.remove());
            showToast('All other devices logged out (Offline)');
        });
    }

    function logoutCurrentSession() {
        showToast('Active authentication session termination is secured', 'warning');
    }

    function fetchDatabaseStats() {
        apiFetch('/api?action=database_stats')
            .then((res) => res.json())
            .then((data) => {
                if (data.error) return;
                if ($('dbName')) $('dbName').textContent = data.name || 'library.db';
                if ($('dbSize')) $('dbSize').textContent = data.size || '—';
                if ($('dbRecords')) $('dbRecords').textContent = data.total_records?.toLocaleString() || '0';
                if ($('dbLastBackup')) $('dbLastBackup').textContent = data.last_backup || 'Never';
                if ($('dbHealth')) {
                    $('dbHealth').innerHTML = `<span class="settings-badge"><i class="fas fa-check-circle"></i> ${data.health || 'Healthy'}</span>`;
                }
            })
            .catch(() => {});
    }

    function fetchBackups() {
        apiFetch('/api?action=get_backups')
            .then(res => res.json())
            .then(data => {
                if (data.error) return;
                renderBackupsUI(data);
            })
            .catch(() => {});
    }

    function renderBackupsUI(backups) {
        const tbody = $('backupsHistoryBody');
        if (!tbody) return;

        if (!backups || backups.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);">No backups found</td></tr>`;
            return;
        }

        tbody.innerHTML = backups.map(b => {
            const deleteButton = `<button type="button" class="settings-btn settings-btn-danger" style="padding:4px 8px; font-size:11px;" onclick="deleteBackup('${b.filename}')"><i class="fas fa-trash"></i> Delete</button>`;
            const getButton = `<button type="button" class="settings-btn settings-btn-primary" style="padding:4px 8px; font-size:11px;" onclick="downloadBackupFile('${b.filename}')"><i class="fas fa-download"></i> Get</button>`;
            
            return `<tr>
                <td><i class="fas fa-database" style="color:var(--neon-blue); margin-right:6px;"></i>${b.filename}</td>
                <td><span class="settings-badge">${b.trigger_type}</span></td>
                <td>${b.size_text}</td>
                <td>${b.created_at}</td>
                <td>
                    <div style="display:flex; gap:8px;">
                        ${getButton}
                        ${deleteButton}
                    </div>
                </td>
            </tr>`;
        }).join('');
    }

    function deleteBackup(filename) {
        if (!confirm(`Are you sure you want to permanently delete backup file: ${filename}?`)) return;
        apiFetch('/api?action=delete_backup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: filename })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
            } else {
                showToast('Backup deleted successfully');
                fetchBackups();
                fetchDatabaseStats();
            }
        })
        .catch(() => showToast('Failed to delete backup', 'error'));
    }

    function downloadBackupFile(filename) {
        window.open(`/api?action=download_backup&filename=${encodeURIComponent(filename)}`, '_blank');
        showToast(`Downloading ${filename}...`);
    }

    function createBackup() {
        showToast('Creating database backup...');
        apiFetch('/api?action=db_backup', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            showToast('Asynchronous database backup is executing.');
            setTimeout(() => {
                fetchDatabaseStats();
                fetchBackups();
                if (auditLoaded) renderAuditLogs();
            }, 3000);
        })
        .catch(() => {
            showToast('Backup failed: Server is offline', 'error');
        });
    }

    function downloadBackup() {
        window.open('/api?action=database_stats', '_blank');
        showToast('Fetching database statistics for download');
    }

    function scheduleBackup() {
        openModal('scheduleBackupModal');
    }

    function confirmScheduleBackup() {
        closeModal('scheduleBackupModal');
        showToast('Backup schedule saved');
        markDirty();
    }

    function prepareRestore(event) {
        const file = event.target.files[0];
        if (!file) return;
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['sql', 'zip', 'db'].includes(ext)) {
            showToast('Only DB, SQL, and ZIP files are supported', 'error');
            event.target.value = '';
            return;
        }
        restoreFile = file;
        $('restoreFileName').textContent = file.name;
        openModal('restoreConfirmModal');
    }

    function confirmRestore() {
        if (!restoreFile) return;
        closeModal('restoreConfirmModal');
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const rawData = e.target.result;
            const b64 = btoa(new Uint8Array(rawData).reduce((data, byte) => data + String.fromCharCode(byte), ''));
            
            showToast('Restoring database from backup file...');
            apiFetch('/api?action=db_restore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file_data: b64, filename: restoreFile.name })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    showToast(data.error, 'error');
                } else {
                    showToast('Database restored successfully! Reloading...');
                    setTimeout(() => location.reload(), 1500);
                }
            })
            .catch(() => {
                showToast('Restore failed: Server is offline', 'error');
            });
            restoreFile = null;
        };
        reader.readAsArrayBuffer(restoreFile);
    }

    function optimizeDatabase() {
        showToast('Optimizing database...');
        apiFetch('/api?action=db_optimize', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            showToast('Database optimization completed');
        })
        .catch(() => {
            showToast('Optimize failed: Server is offline', 'error');
        });
    }

    function clearCache() {
        showToast('Clearing cache...');
        apiFetch('/api?action=db_clear_cache', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            showToast('Cache cleared successfully');
        })
        .catch(() => {
            showToast('Clear cache failed: Server is offline', 'error');
        });
    }

    function repairDatabase() {
        showToast('Repairing database...');
        apiFetch('/api?action=db_repair', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            showToast(`Database integrity checked: ${data.result}`);
        })
        .catch(() => {
            showToast('Repair database failed: Server is offline', 'error');
        });
    }

    function rebuildIndexes() {
        showToast('Rebuilding indexes...');
        apiFetch('/api?action=db_rebuild_indexes', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            showToast('Database indexes rebuilt successfully');
        })
        .catch(() => {
            showToast('Rebuild indexes failed: Server is offline', 'error');
        });
    }

    function getFilteredAuditLogs() {
        const search = ($('auditSearch')?.value || '').toLowerCase();
        const module = $('auditModuleFilter')?.value || 'all';
        const status = $('auditStatusFilter')?.value || 'all';

        return auditLogsFallback.filter((log) => {
            const matchSearch = !search || Object.values(log).some((v) => String(v).toLowerCase().includes(search));
            const matchModule = module === 'all' || log.module === module;
            const matchStatus = status === 'all' || log.status === status;
            return matchSearch && matchModule && matchStatus;
        });
    }

    function renderAuditLogs() {
        const tbody = $('auditLogsBody');
        const pageInfo = $('auditPageInfo');
        if (!tbody) return;

        apiFetch(`/api?action=get_audit_logs`)
            .then(res => res.json())
            .then(logs => {
                if (logs.error) throw new Error(logs.error);
                
                const filtered = logs.filter(log => {
                    const search = ($('auditSearch')?.value || '').toLowerCase();
                    const module = $('auditModuleFilter')?.value || 'all';
                    const matchSearch = !search || Object.values(log).some((v) => String(v).toLowerCase().includes(search));
                    const matchModule = module === 'all' || log.module === module;
                    return matchSearch && matchModule;
                });

                const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
                if (auditPage > totalPages) auditPage = totalPages;

                const start = (auditPage - 1) * PAGE_SIZE;
                const pageItems = filtered.slice(start, start + PAGE_SIZE);

                tbody.innerHTML = pageItems.map((log) => {
                    const badgeClass = log.status === 'Failed' ? 'danger' : log.status === 'Warning' ? 'warning' : '';
                    return `<tr>
                        <td>${log.timestamp}</td>
                        <td>${log.user}</td>
                        <td>${log.action}</td>
                        <td>${log.module}</td>
                        <td>${log.ip}</td>
                        <td><span class="settings-badge ${badgeClass}">${log.status}</span></td>
                    </tr>`;
                }).join('') || '<tr><td colspan="6" style="text-align:center;color:var(--text-secondary);">No audit logs found</td></tr>';

                if (pageInfo) pageInfo.textContent = `Page ${auditPage} of ${totalPages}`;
                $('auditPrevBtn').disabled = auditPage <= 1;
                $('auditNextBtn').disabled = auditPage >= totalPages;
            })
            .catch(() => {
                const filtered = getFilteredAuditLogs();
                const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
                if (auditPage > totalPages) auditPage = totalPages;

                const start = (auditPage - 1) * PAGE_SIZE;
                const pageItems = filtered.slice(start, start + PAGE_SIZE);

                tbody.innerHTML = pageItems.map((log) => {
                    const badgeClass = log.status === 'Failed' ? 'danger' : log.status === 'Warning' ? 'warning' : '';
                    return `<tr>
                        <td>${log.timestamp}</td>
                        <td>${log.user}</td>
                        <td>${log.action}</td>
                        <td>${log.module}</td>
                        <td>${log.ip}</td>
                        <td><span class="settings-badge ${badgeClass}">${log.status}</span></td>
                    </tr>`;
                }).join('') || '<tr><td colspan="6" style="text-align:center;color:var(--text-secondary);">No audit logs found</td></tr>';

                if (pageInfo) pageInfo.textContent = `Page ${auditPage} of ${totalPages}`;
                $('auditPrevBtn').disabled = auditPage <= 1;
                $('auditNextBtn').disabled = auditPage >= totalPages;
            });
    }

    function exportAuditLogs() {
        apiFetch(`/api?action=get_audit_logs`)
            .then(res => res.json())
            .then(logs => {
                if (logs.error) throw new Error(logs.error);
                const header = 'Timestamp,User,Action,Module,IP Address,Status\n';
                const rows = logs.map((l) => `"${l.timestamp}","${l.user}","${l.action}","${l.module}","${l.ip}","${l.status}"`).join('\n');
                const blob = new Blob([header + rows], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'audit_logs.csv';
                a.click();
                URL.revokeObjectURL(url);
                showToast('Audit logs exported successfully');
            })
            .catch(() => {
                showToast('Failed to export audit logs: Server is offline', 'error');
            });
    }

    function initThemeToggle() {
        const toggle = $('settingsThemeToggle');
        if (!toggle) return;

        const syncIcon = () => {
            const isLight = document.body.classList.contains('light-mode');
            toggle.classList.toggle('active', isLight);
            const icon = toggle.querySelector('i');
            if (icon) icon.className = isLight ? 'fas fa-sun' : 'fas fa-moon';
            toggle.setAttribute('aria-pressed', isLight ? 'true' : 'false');
        };

        syncIcon();
        toggle.addEventListener('click', () => {
            document.body.classList.toggle('light-mode');
            localStorage.setItem('theme', document.body.classList.contains('light-mode') ? 'light' : 'dark');
            syncIcon();
            showToast(document.body.classList.contains('light-mode') ? 'Light mode enabled' : 'Dark mode enabled');
        });
    }

    function bindEvents() {
        document.querySelectorAll('.settings-menu-item').forEach((btn) => {
            btn.addEventListener('click', () => trySwitchTab(btn.dataset.tab));
        });

        $('saveSettingsBtn')?.addEventListener('click', saveSettings);

        document.querySelectorAll('.settings-track-change').forEach((el) => {
            el.addEventListener('input', markDirty);
            el.addEventListener('change', markDirty);
        });

        document.querySelectorAll('.color-dot').forEach((btn) => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.color-dot').forEach((d) => {
                    d.classList.remove('active');
                    d.style.borderColor = 'transparent';
                });
                btn.classList.add('active');
                btn.style.borderColor = 'white';
                updatePreviewUI();
                markDirty();
            });
        });

        const customizationFields = ['fontFamily', 'uiDensity', 'glassmorphism', 'animationsEnabled', 'fontSize', 'fontWeight', 'letterSpacing', 'lineHeight', 'visualMode'];
        customizationFields.forEach((id) => {
            $(id)?.addEventListener('change', () => {
                updatePreviewUI();
                markDirty();
            });
        });

        const realtimeFields = [
            { id: 'email', type: 'email', message: 'Enter a valid email address', errorId: 'emailError' },
            { id: 'phone', type: 'phone', message: 'Enter a valid phone number', errorId: 'phoneError' },
            { id: 'fullName', type: 'required', message: 'Full name is required', errorId: 'fullNameError' },
            { id: 'username', type: 'required', message: 'Username is required', errorId: 'usernameError' }
        ];
        realtimeFields.forEach(({ id, type, message, errorId }) => {
            $(id)?.addEventListener('blur', (e) => validateField(e.target, type, message, errorId));
        });

        $('newPassword')?.addEventListener('input', checkPasswordStrength);
        $('confirmPassword')?.addEventListener('input', validatePasswordMatch);

        $('auditSearch')?.addEventListener('input', () => { auditPage = 1; renderAuditLogs(); });
        $('auditModuleFilter')?.addEventListener('change', () => { auditPage = 1; renderAuditLogs(); });
        $('auditStatusFilter')?.addEventListener('change', () => { auditPage = 1; renderAuditLogs(); });
        $('auditSearchBtn')?.addEventListener('click', renderAuditLogs);
        $('auditPrevBtn')?.addEventListener('click', () => { auditPage--; renderAuditLogs(); });
        $('auditNextBtn')?.addEventListener('click', () => { auditPage++; renderAuditLogs(); });

        $('unsavedSaveBtn')?.addEventListener('click', () => {
            saveSettings();
            closeModal('unsavedModal');
            if (pendingTab) { openTab(pendingTab); pendingTab = null; }
        });
        $('unsavedDiscardBtn')?.addEventListener('click', () => {
            markClean();
            loadSettings();
            closeModal('unsavedModal');
            if (pendingTab) { openTab(pendingTab); pendingTab = null; }
        });

        const uploadZone = $('restoreUploadZone');
        if (uploadZone) {
            ['dragenter', 'dragover'].forEach((ev) => {
                uploadZone.addEventListener(ev, (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
            });
            ['dragleave', 'drop'].forEach((ev) => {
                uploadZone.addEventListener(ev, (e) => { e.preventDefault(); uploadZone.classList.remove('dragover'); });
            });
            uploadZone.addEventListener('drop', (e) => {
                const file = e.dataTransfer.files[0];
                if (file) prepareRestore({ target: { files: [file] } });
            });
        }

        // Avatar Crop Controls binding
        $('cropZoomSlider')?.addEventListener('input', (e) => {
            cropZoom = parseFloat(e.target.value);
            drawCropCanvas();
        });

        $('cropRotateLeftBtn')?.addEventListener('click', () => {
            cropRotation = (cropRotation - 90) % 360;
            drawCropCanvas();
        });

        $('cropRotateRightBtn')?.addEventListener('click', () => {
            cropRotation = (cropRotation + 90) % 360;
            drawCropCanvas();
        });

        $('cropSaveBtn')?.addEventListener('click', saveCrop);

        const cropCanvas = $('cropCanvas');
        if (cropCanvas) {
            cropCanvas.addEventListener('mousedown', (e) => {
                isDragging = true;
                startX = e.clientX - imgX;
                startY = e.clientY - imgY;
                cropCanvas.style.cursor = 'grabbing';
            });

            window.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                imgX = e.clientX - startX;
                imgY = e.clientY - startY;
                drawCropCanvas();
            });

            window.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    cropCanvas.style.cursor = 'move';
                }
            });

            cropCanvas.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    isDragging = true;
                    startX = e.touches[0].clientX - imgX;
                    startY = e.touches[0].clientY - imgY;
                }
            });

            window.addEventListener('touchmove', (e) => {
                if (!isDragging) return;
                if (e.touches.length === 1) {
                    imgX = e.touches[0].clientX - startX;
                    imgY = e.touches[0].clientY - startY;
                    drawCropCanvas();
                }
            });

            window.addEventListener('touchend', () => {
                isDragging = false;
            });
        }

        // Avatar drag and drop uploading
        const avatarDisplay = $('avatarDisplay');
        if (avatarDisplay) {
            ['dragenter', 'dragover'].forEach((ev) => {
                avatarDisplay.addEventListener(ev, (e) => {
                    e.preventDefault();
                    avatarDisplay.style.border = '2px dashed var(--neon-blue)';
                    avatarDisplay.style.background = 'rgba(0, 210, 255, 0.1)';
                });
            });
            ['dragleave', 'drop'].forEach((ev) => {
                avatarDisplay.addEventListener(ev, (e) => {
                    e.preventDefault();
                    avatarDisplay.style.border = 'none';
                    avatarDisplay.style.background = '';
                });
            });
            avatarDisplay.addEventListener('drop', (e) => {
                const file = e.dataTransfer.files[0];
                if (file) {
                    previewAvatar({ target: { files: [file] } });
                }
            });
        }

        window.addEventListener('beforeunload', (e) => {
            if (hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.settings-modal.active').forEach((m) => {
                    m.classList.remove('active');
                    m.setAttribute('aria-hidden', 'true');
                });
            }
        });
    }

    window.previewAvatar = previewAvatar;
    window.removeAvatar = removeAvatar;
    window.togglePasswordVisibility = togglePasswordVisibility;
    window.changePassword = changePassword;
    window.generateRecoveryCodes = generateRecoveryCodes;
    window.logoutDevice = logoutDevice;
    window.logoutAllDevices = logoutAllDevices;
    window.logoutCurrentSession = logoutCurrentSession;
    window.createBackup = createBackup;
    window.downloadBackup = downloadBackup;
    window.scheduleBackup = scheduleBackup;
    window.confirmScheduleBackup = confirmScheduleBackup;
    window.prepareRestore = prepareRestore;
    window.confirmRestore = confirmRestore;
    window.restoreDatabase = () => openModal('restoreConfirmModal');
    window.optimizeDatabase = optimizeDatabase;
    window.clearCache = clearCache;
    window.repairDatabase = repairDatabase;
    window.rebuildIndexes = rebuildIndexes;
    window.exportAuditLogs = exportAuditLogs;
    window.closeSettingsModal = (id) => closeModal(id);
    window.saveSettings = saveSettings;
    window.toggleIdFields = toggleIdFields;
    window.deleteBackup = deleteBackup;
    window.downloadBackupFile = downloadBackupFile;

    document.addEventListener('DOMContentLoaded', () => {
        loadSettings();
        fetchDatabaseStats();
        initThemeToggle();
        bindEvents();
        updatePreviewUI();
    });
})();
