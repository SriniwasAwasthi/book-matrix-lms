(function() {
    'use strict';

    // 1. Get saved customization state from localStorage (fast sync)
    const settingsStr = localStorage.getItem('bookMatrixSettings');
    if (settingsStr) {
        try {
            const settings = JSON.parse(settingsStr);
            const custom = settings.customization || {};
            const root = document.documentElement;

            // Apply accent color
            const colors = {
                blue: '#00d2ff',
                purple: '#9d50bb',
                emerald: '#00ff87',
                rose: '#ff416c',
                orange: '#ff8c00'
            };
            const activeColor = colors[custom.accentColor] || colors.blue;
            root.style.setProperty('--neon-blue', activeColor);

            // Apply font family
            const fonts = {
                cinzel: "'Cinzel', serif",
                inter: "'Inter', sans-serif",
                outfit: "'Outfit', sans-serif",
                montserrat: "'Montserrat', sans-serif",
                roboto: "'Roboto', sans-serif"
            };
            const activeFont = fonts[custom.fontFamily] || fonts.cinzel;
            root.style.setProperty('--font-body', activeFont);

            // Apply visual mode immediately to root and on DOMContentLoaded to body
            const theme = custom.visualMode || 'dark';
            if (theme === 'light') {
                root.classList.add('light-mode');
            } else {
                root.classList.remove('light-mode');
            }

            document.addEventListener('DOMContentLoaded', () => {
                if (theme === 'light') {
                    document.body.classList.add('light-mode');
                } else {
                    document.body.classList.remove('light-mode');
                }
            });

            // Apply glassmorphism
            if (custom.glassmorphism === false) {
                root.style.setProperty('--glass-bg', 'rgba(0, 0, 0, 0.3)');
                root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.05)');
            } else {
                root.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.05)');
                root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.1)');
            }

            // Apply typography overrides
            if (custom.fontSize) {
                root.style.setProperty('--font-size-base', custom.fontSize);
            }
            if (custom.fontWeight) {
                root.style.setProperty('--font-weight-base', custom.fontWeight);
            }
            if (custom.letterSpacing) {
                root.style.setProperty('--letter-spacing-base', custom.letterSpacing);
            }
            if (custom.lineHeight) {
                root.style.setProperty('--line-height-base', custom.lineHeight);
            }

        } catch (e) {
            console.warn('Theme loading error:', e);
        }
    } else {
        // Fallback for simple toggle
        const simpleTheme = localStorage.getItem('theme');
        if (simpleTheme === 'light') {
            document.documentElement.classList.add('light-mode');
            document.addEventListener('DOMContentLoaded', () => {
                document.body.classList.add('light-mode');
            });
        }
    }
})();
