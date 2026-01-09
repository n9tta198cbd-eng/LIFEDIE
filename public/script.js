document.addEventListener('DOMContentLoaded', () => {
    const baseUrl = window.location.origin;
    const presets = {
        '1320x2868': { w: 1320, h: 2868 },
        '1206x2622': { w: 1206, h: 2622 },
        '1179x2556': { w: 1179, h: 2556 },
        '1290x2796': { w: 1290, h: 2796 },
    };

    // Generate preview dots
    generatePreviewDots();

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
        const lifeDevice = presets[document.getElementById('life-device').value];

        if (lifeYear && lifeMonth && lifeDay) {
            const lifeParams = new URLSearchParams({
                type: 'life',
                birth: `${lifeYear}-${pad(lifeMonth)}-${pad(lifeDay)}`,
                lifespan: lifeExpectancy,
                w: lifeDevice.w,
                h: lifeDevice.h
            });
            document.getElementById('life-url').value = `${baseUrl}/api/generate?${lifeParams}`;
        }

        // Year Calendar URL
        const yearDevice = presets[document.getElementById('year-device').value];
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
        const goalDevice = presets[document.getElementById('goal-device').value];

        if (goalStartYear && goalEndYear) {
            const goalParams = new URLSearchParams({
                type: 'goal',
                goal: goalName,
                start: `${goalStartYear}-${pad(goalStartMonth)}-${pad(goalStartDay)}`,
                deadline: `${goalEndYear}-${pad(goalEndMonth)}-${pad(goalEndDay)}`,
                w: goalDevice.w,
                h: goalDevice.h
            });
            document.getElementById('goal-url').value = `${baseUrl}/api/generate?${goalParams}`;
        }
    }

    function pad(n) {
        return String(n).padStart(2, '0');
    }

    function generatePreviewDots() {
        // Life dots (52x20 = 1040 weeks ~ 20 years shown)
        const lifeDots = document.querySelector('.life-dots');
        for (let i = 0; i < 52 * 20; i++) {
            const dot = document.createElement('div');
            dot.className = 'dot' + (i < 52 * 8 ? ' filled' : '');
            lifeDots.appendChild(dot);
        }

        // Year dots (14x26 = 364 days)
        const yearDots = document.querySelector('.year-dots');
        const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 86400000);
        for (let i = 0; i < 14 * 26; i++) {
            const dot = document.createElement('div');
            dot.className = 'dot' + (i < dayOfYear ? ' filled' : i === dayOfYear ? ' current' : '');
            yearDots.appendChild(dot);
        }

        // Goal dots (7x10 = 70 days)
        const goalDots = document.querySelector('.goal-dots');
        for (let i = 0; i < 7 * 10; i++) {
            const dot = document.createElement('div');
            dot.className = 'dot' + (i < 5 ? ' filled' : i === 5 ? ' current' : '');
            goalDots.appendChild(dot);
        }
    }

    // Initial URL generation
    updateUrls();
});
