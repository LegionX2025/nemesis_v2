
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { 
                        sans: ['Inter', 'sans-serif'], 
                        mono: ['JetBrains Mono', 'monospace'],
                        serif: ['Playfair Display', 'serif'],
                        cyber: ['Syncopate', 'sans-serif']
                    },
                    colors: { 
                        nemesis: { light: '#f8fafc', panel: '#ffffff', border: '#e2e8f0', accent: '#2563eb', glow: '#bfdbfe' },
                        danger: { 50: '#fef2f2', 500: '#ef4444', 600: '#dc2626', 900: '#7f1d1d' }
                    },
                    animation: {
                        'pulse-fast': 'pulse 1.2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                        'scanline': 'scanline 8s linear infinite',
                        'data-stream': 'dataStream 0.5s infinite alternate',
                        'gradient-xy': 'gradient-xy 3s ease infinite',
                    },
                    keyframes: {
                        dataStream: { '0%': { opacity: 0.3 }, '100%': { opacity: 1 } },
                        'gradient-xy': {
                            '0%, 100%': {
                                'background-size': '400% 400%',
                                'background-position': 'left center'
                            },
                            '50%': {
                                'background-size': '200% 200%',
                                'background-position': 'right center'
                            }
                        }
                    }
                }
            }
        }
    