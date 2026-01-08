document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('calendar-form');
    const deviceSelect = document.getElementById('device');
    const customSizeDiv = document.getElementById('custom-size');
    const widthInput = document.getElementById('width');
    const heightInput = document.getElementById('height');
    const resultDiv = document.getElementById('result');
    const generatedLinkInput = document.getElementById('generated-link');
    const copyBtn = document.getElementById('copy-btn');
    const previewImg = document.getElementById('preview-img');
    const previewLink = document.getElementById('preview-link');

    // Device presets
    const presets = {
        '1320x2868': { w: 1320, h: 2868 }, // iPhone 16 Pro Max
        '1206x2622': { w: 1206, h: 2622 }, // iPhone 16 Pro
        '1290x2796': { w: 1290, h: 2796 }, // iPhone 15/14 Pro Max
        '1179x2556': { w: 1179, h: 2556 }, // iPhone 15/14 Pro
        '1170x2532': { w: 1170, h: 2532 }, // iPhone 14/13/12
    };

    // Toggle custom size inputs
    deviceSelect.addEventListener('change', () => {
        if (deviceSelect.value === 'custom') {
            customSizeDiv.style.display = 'block';
        } else {
            customSizeDiv.style.display = 'none';
            const preset = presets[deviceSelect.value];
            if (preset) {
                widthInput.value = preset.w;
                heightInput.value = preset.h;
            }
        }
    });

    // Form submit
    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const birth = document.getElementById('birth').value;
        const lifespan = document.getElementById('lifespan').value;

        let w, h;
        if (deviceSelect.value === 'custom') {
            w = widthInput.value;
            h = heightInput.value;
        } else {
            const preset = presets[deviceSelect.value];
            w = preset.w;
            h = preset.h;
        }

        // Build URL
        const baseUrl = window.location.origin;
        const params = new URLSearchParams({
            birth: birth,
            lifespan: lifespan,
            w: w,
            h: h
        });

        const fullUrl = `${baseUrl}/generate?${params.toString()}`;

        // Show result
        generatedLinkInput.value = fullUrl;
        resultDiv.style.display = 'block';

        // Update preview (smaller version)
        const previewParams = new URLSearchParams({
            birth: birth,
            lifespan: lifespan,
            w: Math.min(w, 400),
            h: Math.round(Math.min(w, 400) * (h / w))
        });
        const previewUrl = `${baseUrl}/generate?${previewParams.toString()}`;
        previewImg.src = previewUrl;
        previewLink.href = fullUrl;

        // Scroll to result
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    });

    // Copy to clipboard
    copyBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(generatedLinkInput.value);
            copyBtn.textContent = 'Copied!';
            copyBtn.classList.add('copied');
            setTimeout(() => {
                copyBtn.textContent = 'Copy';
                copyBtn.classList.remove('copied');
            }, 2000);
        } catch (err) {
            // Fallback
            generatedLinkInput.select();
            document.execCommand('copy');
            copyBtn.textContent = 'Copied!';
            copyBtn.classList.add('copied');
            setTimeout(() => {
                copyBtn.textContent = 'Copy';
                copyBtn.classList.remove('copied');
            }, 2000);
        }
    });
});
