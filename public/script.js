document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const openModalBtn = document.getElementById('open-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const modalOverlay = document.getElementById('modal-overlay');
    const generatedUrlInput = document.getElementById('generated-url');
    const copyBtn = document.getElementById('copy-btn');

    // Form fields
    const goalInput = document.getElementById('goal');
    const startYear = document.getElementById('start-year');
    const startMonth = document.getElementById('start-month');
    const startDay = document.getElementById('start-day');
    const deadlineYear = document.getElementById('deadline-year');
    const deadlineMonth = document.getElementById('deadline-month');
    const deadlineDay = document.getElementById('deadline-day');
    const deviceSelect = document.getElementById('device');

    // Device presets
    const presets = {
        '1320x2868': { w: 1320, h: 2868 },
        '1206x2622': { w: 1206, h: 2622 },
        '1179x2556': { w: 1179, h: 2556 },
        '1290x2796': { w: 1290, h: 2796 },
        '1170x2532': { w: 1170, h: 2532 },
    };

    // Set default dates
    const today = new Date();
    startYear.value = today.getFullYear();
    startMonth.value = String(today.getMonth() + 1).padStart(2, '0');
    startDay.value = String(today.getDate()).padStart(2, '0');

    const nextMonth = new Date(today);
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    deadlineYear.value = nextMonth.getFullYear();
    deadlineMonth.value = String(nextMonth.getMonth() + 1).padStart(2, '0');
    deadlineDay.value = String(nextMonth.getDate()).padStart(2, '0');

    // Open modal
    openModalBtn.addEventListener('click', () => {
        modalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        updateUrl();
    });

    // Close modal
    closeModalBtn.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    });

    function closeModal() {
        modalOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
            closeModal();
        }
    });

    // Update URL when any field changes
    const allInputs = [goalInput, startYear, startMonth, startDay, deadlineYear, deadlineMonth, deadlineDay, deviceSelect];
    allInputs.forEach(input => {
        input.addEventListener('input', updateUrl);
        input.addEventListener('change', updateUrl);
    });

    function updateUrl() {
        const goal = goalInput.value || 'My Goal';
        const start = `${startYear.value}-${pad(startMonth.value)}-${pad(startDay.value)}`;
        const deadline = `${deadlineYear.value}-${pad(deadlineMonth.value)}-${pad(deadlineDay.value)}`;
        const preset = presets[deviceSelect.value];
        const w = preset.w;
        const h = preset.h;

        const baseUrl = window.location.origin;
        const params = new URLSearchParams({
            goal: goal,
            start: start,
            deadline: deadline,
            w: w,
            h: h
        });

        generatedUrlInput.value = `${baseUrl}/api/generate?${params.toString()}`;
    }

    function pad(num) {
        return String(num).padStart(2, '0');
    }

    // Copy to clipboard
    copyBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(generatedUrlInput.value);
            showCopied();
        } catch (err) {
            // Fallback
            generatedUrlInput.select();
            document.execCommand('copy');
            showCopied();
        }
    });

    function showCopied() {
        copyBtn.classList.add('copied');
        copyBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
        setTimeout(() => {
            copyBtn.classList.remove('copied');
            copyBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
        }, 2000);
    }

    // Initial URL generation
    updateUrl();
});
