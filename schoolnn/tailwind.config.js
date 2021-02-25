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
        "accent": "#109CF1", // Buttons
        "accent-hover": "#34AFF9", // Buttons on hover
        "accent-focus": "#098EDF", // Buttons on click
        "light-gray": "#F1F3F5",
        "text-gray": "#90A0B7",
        "black": "#192A3E",
        "icon-gray": "#90A0B7",
        "green": "#2ED47A",
        "light-green": "rgba(46, 212, 122, 0.9)",
        "yellow": "#FFB946",
        "red": "#F7685B",
      },

      spacing: {
        "screen-minus-header": "calc(100vh - 6rem)",
      },

      boxShadow: {
        "base": "6px 6px 18px rgba(0, 0, 0, 0.06)",
        "button": "0px 4px 10px rgba(16, 156, 241, 0.24);",
        "button-hover": "0px 8px 16px rgba(52, 175, 249, 0.2);",
        "button-focus": "0px 2px 6px rgba(9, 142, 223, 0.3);",
      },

      fontFamily: {
        "sans": ['"Poppins"', 'sans-serif'],
      },

      minHeight: {
        '4': '1rem',
        "screen-minus-header": "calc(100vh - 6rem)",
      }
    },
  },
  variants: {},
  plugins: [],
}
