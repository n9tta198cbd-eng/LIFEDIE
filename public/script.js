// Language Toggle
class LanguageToggle {
    constructor() {
        this.currentLang = localStorage.getItem('selectedLanguage') || 'ru';
        this.init();
    }

    init() {
        // Set initial language
        this.setLanguage(this.currentLang, false);

        // Add click listeners to language buttons
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const lang = btn.dataset.lang;
                this.setLanguage(lang);
            });
        });
    }

    setLanguage(lang, save = true) {
        this.currentLang = lang;

        // Update active button
        document.querySelectorAll('.lang-btn').forEach(btn => {
            if (btn.dataset.lang === lang) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Show/hide text based on language
        document.querySelectorAll('[data-lang-text]').forEach(el => {
            if (el.dataset.langText === lang) {
                el.classList.remove('hidden');
            } else {
                el.classList.add('hidden');
            }
        });

        // Save to localStorage
        if (save) {
            localStorage.setItem('selectedLanguage', lang);
        }
    }
}

// Initialize language toggle when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new LanguageToggle();

    const baseUrl = window.location.origin;
    const presets = {
        '1080x2340': { w: 1080, h: 2340 },
        '1170x2532': { w: 1170, h: 2532 },
        '1284x2778': { w: 1284, h: 2778 },
        '1179x2556': { w: 1179, h: 2556 },
        '1290x2796': { w: 1290, h: 2796 },
        '1206x2622': { w: 1206, h: 2622 },
        '1320x2868': { w: 1320, h: 2868 },
    };

    // Modal handling
    document.querySelectorAll('[data-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.dataset.modal;
            const modal = document.getElementById(`modal-${modalId}`);
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            updateUrls();
        });
    });

    document.querySelectorAll('[data-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal-overlay').classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                modal.classList.remove('active');
            });
            document.body.style.overflow = '';
        }
    });

    // Copy buttons
    document.querySelectorAll('.btn-copy').forEach(btn => {
        btn.addEventListener('click', async () => {
            const targetId = btn.dataset.target;
            const input = document.getElementById(targetId);
            try {
                await navigator.clipboard.writeText(input.value);
                showCopied(btn);
            } catch {
                input.select();
                document.execCommand('copy');
                showCopied(btn);
            }
        });
    });

    function showCopied(btn) {
        btn.classList.add('copied');
        btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
        setTimeout(() => {
            btn.classList.remove('copied');
            btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
        }, 2000);
    }

    // Date validation
    function isValidDate(year, month, day) {
        const y = parseInt(year);
        const m = parseInt(month);
        const d = parseInt(day);

        if (isNaN(y) || isNaN(m) || isNaN(d)) return false;
        if (y < 1900 || y > 2100) return false;
        if (m < 1 || m > 12) return false;
        if (d < 1 || d > 31) return false;

        // Check days in month
        const daysInMonth = new Date(y, m, 0).getDate();
        if (d > daysInMonth) return false;

        return true;
    }

    function clampValue(input, min, max) {
        let val = parseInt(input.value);
        if (isNaN(val)) return;
        if (val < min) input.value = min;
        if (val > max) input.value = max;
    }

    // Add validation on blur for date inputs
    document.querySelectorAll('.date-inputs input').forEach(input => {
        input.addEventListener('blur', () => {
            const placeholder = input.placeholder;
            if (placeholder === '1990' || placeholder === '2026') {
                clampValue(input, 1900, 2100);
            } else if (placeholder === '01' && input.id.includes('month')) {
                clampValue(input, 1, 12);
            } else if (placeholder === '01' || placeholder === '31' || placeholder === '12') {
                clampValue(input, 1, 31);
            }
        });
    });

    // Set default dates
    const today = new Date();
    const nextMonth = new Date(today);
    nextMonth.setMonth(nextMonth.getMonth() + 3);

    // Life form defaults
    document.getElementById('life-year').value = '1990';
    document.getElementById('life-month').value = '01';
    document.getElementById('life-day').value = '01';

    // Goal form defaults
    document.getElementById('goal-start-year').value = today.getFullYear();
    document.getElementById('goal-start-month').value = pad(today.getMonth() + 1);
    document.getElementById('goal-start-day').value = pad(today.getDate());
    document.getElementById('goal-end-year').value = nextMonth.getFullYear();
    document.getElementById('goal-end-month').value = pad(nextMonth.getMonth() + 1);
    document.getElementById('goal-end-day').value = pad(nextMonth.getDate());

    // Update URLs on input change
    document.querySelectorAll('input, select').forEach(el => {
        el.addEventListener('input', updateUrls);
        el.addEventListener('change', updateUrls);
    });

    function updateUrls() {
        // Life Calendar URL
        const lifeYear = document.getElementById('life-year').value;
        const lifeMonth = document.getElementById('life-month').value;
        const lifeDay = document.getElementById('life-day').value;
        const lifeExpectancy = document.getElementById('life-expectancy').value;
        const lifeDeviceValue = document.getElementById('life-device').value;
        const lifeDevice = presets[lifeDeviceValue] || presets['1179x2556'];

        if (lifeYear && lifeMonth && lifeDay && isValidDate(lifeYear, lifeMonth, lifeDay)) {
            const lifeParams = new URLSearchParams({
                type: 'life',
                birth: `${lifeYear}-${pad(lifeMonth)}-${pad(lifeDay)}`,
                lifespan: lifeExpectancy,
                w: lifeDevice.w,
                h: lifeDevice.h
            });
            document.getElementById('life-url').value = `${baseUrl}/api/generate?${lifeParams}`;
        } else {
            document.getElementById('life-url').value = 'Complete step 1 first...';
        }

        // Year Calendar URL
        const yearDeviceValue = document.getElementById('year-device').value;
        const yearDevice = presets[yearDeviceValue] || presets['1179x2556'];
        const yearParams = new URLSearchParams({
            type: 'year',
            w: yearDevice.w,
            h: yearDevice.h
        });
        document.getElementById('year-url').value = `${baseUrl}/api/generate?${yearParams}`;

        // Goal Calendar URL
        const goalName = document.getElementById('goal-name').value || 'My Goal';
        const goalStartYear = document.getElementById('goal-start-year').value;
        const goalStartMonth = document.getElementById('goal-start-month').value;
        const goalStartDay = document.getElementById('goal-start-day').value;
        const goalEndYear = document.getElementById('goal-end-year').value;
        const goalEndMonth = document.getElementById('goal-end-month').value;
        const goalEndDay = document.getElementById('goal-end-day').value;
        const goalDeviceValue = document.getElementById('goal-device').value;
        const goalDevice = presets[goalDeviceValue] || presets['1179x2556'];

        const startValid = isValidDate(goalStartYear, goalStartMonth, goalStartDay);
        const endValid = isValidDate(goalEndYear, goalEndMonth, goalEndDay);

        if (startValid && endValid) {
            const goalParams = new URLSearchParams({
                type: 'goal',
                goal: goalName,
                start: `${goalStartYear}-${pad(goalStartMonth)}-${pad(goalStartDay)}`,
                deadline: `${goalEndYear}-${pad(goalEndMonth)}-${pad(goalEndDay)}`,
                w: goalDevice.w,
                h: goalDevice.h
            });
            document.getElementById('goal-url').value = `${baseUrl}/api/generate?${goalParams}`;
        } else {
            document.getElementById('goal-url').value = 'Complete step 1 first...';
        }
    }

    function pad(n) {
        return String(n).padStart(2, '0');
    }

    // Initial URL generation
    updateUrls();
});
