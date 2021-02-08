module.exports = {
    future: {
        removeDeprecatedGapUtilities: true,
        purgeLayersByDefault: true,
    },
    purge: {
        enabled: false, //true for production build
        content: [
            'templates/*.html',
            'templates/**/*.html'
        ]
    },
    theme: {
        extend: {
            colors: {
                "primary": "#334D6E",
                "light-gray": "#F1F3F5",
                "text-gray": "#90A0B7",
                "black": "#192A3E",
                "selected": "#109CF1",
                "green": "#2ED47A"
            },

            spacing: {
                "screen-minus-header": "calc(100vh - 6rem)",
            },

            boxShadow: {
                "base": "6px 6px 18px rgba(0, 0, 0, 0.06)",
            },

            fontFamily: {
                "sans": ['"Poppins"', 'sans-serif'],
            }
        },
    },
    variants: {},
    plugins: [],
}
