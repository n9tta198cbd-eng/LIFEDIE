/**
 * ANIMATED BACKGROUND - Generative procedural blob animation
 * Creates slow-moving, blurred light blobs on black background
 */

class AnimatedBackground {
    constructor() {
        this.canvas = document.getElementById('bg-canvas');
        if (!this.canvas) {
            console.warn('Background canvas not found');
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        this.blobs = [];
        this.animationId = null;
        this.time = 0;

        // Check if user prefers reduced motion
        this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        this.init();
    }

    init() {
        this.resize();
        this.createBlobs();

        // Event listeners
        window.addEventListener('resize', () => this.resize());

        // Start animation if not reduced motion
        if (!this.prefersReducedMotion) {
            this.animate();
        } else {
            // Draw static blobs for reduced motion
            this.drawFrame();
        }
    }

    resize() {
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.getBoundingClientRect();

        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;

        this.ctx.scale(dpr, dpr);

        this.width = rect.width;
        this.height = rect.height;
    }

    createBlobs() {
        const blobCount = this.width < 768 ? 3 : 5; // Less blobs on mobile

        this.blobs = [];

        for (let i = 0; i < blobCount; i++) {
            this.blobs.push({
                x: Math.random() * this.width,
                y: Math.random() * this.height,
                baseX: Math.random() * this.width,
                baseY: Math.random() * this.height,
                radius: this.random(200, 400),
                speedX: this.random(-0.3, 0.3),
                speedY: this.random(-0.3, 0.3),
                phase: Math.random() * Math.PI * 2,
                frequency: this.random(0.001, 0.003),
                opacity: this.random(0.08, 0.15),
                color: this.getRandomColor()
            });
        }
    }

    getRandomColor() {
        // Серо-белые градиенты с легкими оттенками
        const colors = [
            'rgba(255, 255, 255, 1)',
            'rgba(220, 220, 220, 1)',
            'rgba(200, 200, 200, 1)',
            'rgba(180, 180, 180, 1)'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    random(min, max) {
        return Math.random() * (max - min) + min;
    }

    // Perlin-like noise simulation for organic movement
    noise(x, y, time) {
        return Math.sin(x * 0.01 + time) * Math.cos(y * 0.01 + time);
    }

    updateBlobs() {
        this.time += 0.001;

        this.blobs.forEach(blob => {
            // Organic movement using sine waves
            const noiseX = this.noise(blob.baseX, blob.baseY, this.time);
            const noiseY = this.noise(blob.baseY, blob.baseX, this.time + 100);

            blob.x = blob.baseX + Math.sin(this.time * blob.frequency + blob.phase) * 150 + noiseX * 50;
            blob.y = blob.baseY + Math.cos(this.time * blob.frequency + blob.phase) * 150 + noiseY * 50;

            // Morph radius slightly
            const radiusOffset = Math.sin(this.time * blob.frequency * 2) * 50;
            blob.currentRadius = blob.radius + radiusOffset;

            // Keep blobs in bounds (with margin)
            if (blob.x < -blob.radius * 0.5) blob.baseX = this.width + blob.radius * 0.5;
            if (blob.x > this.width + blob.radius * 0.5) blob.baseX = -blob.radius * 0.5;
            if (blob.y < -blob.radius * 0.5) blob.baseY = this.height + blob.radius * 0.5;
            if (blob.y > this.height + blob.radius * 0.5) blob.baseY = -blob.radius * 0.5;
        });
    }

    drawFrame() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.width, this.height);

        // Apply blur filter
        this.ctx.filter = 'blur(100px)';

        // Draw blobs
        this.blobs.forEach(blob => {
            const gradient = this.ctx.createRadialGradient(
                blob.x, blob.y, 0,
                blob.x, blob.y, blob.currentRadius || blob.radius
            );

            gradient.addColorStop(0, blob.color.replace('1)', `${blob.opacity})`));
            gradient.addColorStop(0.5, blob.color.replace('1)', `${blob.opacity * 0.5})`));
            gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(blob.x, blob.y, blob.currentRadius || blob.radius, 0, Math.PI * 2);
            this.ctx.fill();
        });

        // Reset filter
        this.ctx.filter = 'none';
    }

    animate() {
        this.updateBlobs();
        this.drawFrame();

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        window.removeEventListener('resize', () => this.resize());
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.animatedBackground = new AnimatedBackground();
    });
} else {
    window.animatedBackground = new AnimatedBackground();
}
