/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
      extend: {
          "colors": {
              "primary-fixed-dim": "#aacdce",
              "on-surface": "#191c20",
              "surface-dim": "#d9dadf",
              "secondary-container": "#cbe4e6",
              "on-tertiary-fixed-variant": "#3e494a",
              "inverse-surface": "#2e3035",
              "on-secondary-container": "#506769",
              "on-tertiary-container": "#7f8b8c",
              "surface-container-lowest": "#ffffff",
              "on-tertiary": "#ffffff",
              "on-secondary-fixed-variant": "#344b4d",
              "on-primary": "#ffffff",
              "inverse-primary": "#aacdce",
              "surface-container-highest": "#e2e2e8",
              "on-primary-container": "#6d8f90",
              "secondary-fixed-dim": "#b2cbcd",
              "surface-container-low": "#f3f3f9",
              "surface-container-high": "#e7e8ee",
              "tertiary-fixed-dim": "#bdc9ca",
              "surface-tint": "#436465",
              "tertiary": "#030c0d",
              "background": "#f9f9ff",
              "tertiary-fixed": "#d9e5e6",
              "surface": "#f9f9ff",
              "on-error-container": "#93000a",
              "surface-variant": "#e2e2e8",
              "inverse-on-surface": "#f0f0f6",
              "on-surface-variant": "#414848",
              "tertiary-container": "#182324",
              "error": "#ba1a1a",
              "on-error": "#ffffff",
              "on-secondary": "#ffffff",
              "surface-container": "#ededf3",
              "on-primary-fixed": "#002021",
              "secondary": "#4b6264",
              "on-primary-fixed-variant": "#2b4c4d",
              "primary-container": "#002627",
              "on-background": "#191c20",
              "primary-fixed": "#c5e9ea",
              "error-container": "#ffdad6",
              "outline": "#717878",
              "outline-variant": "#c1c8c8",
              "primary": "#000d0d",
              "secondary-fixed": "#cee7e9",
              "on-secondary-fixed": "#071f21",
              "on-tertiary-fixed": "#131d1e",
              "surface-bright": "#f9f9ff"
          },
          "borderRadius": {
              "DEFAULT": "0.125rem",
              "lg": "0.25rem",
              "xl": "0.5rem",
              "full": "0.75rem"
          },
          "spacing": {
              "container-max": "1120px",
              "unit": "4px",
              "gutter": "24px",
              "margin-desktop": "64px",
              "margin-mobile": "20px"
          },
          "fontFamily": {
              "body-md": ["Hanken Grotesk"],
              "label-sm": ["Hanken Grotesk"],
              "label-md": ["Hanken Grotesk"],
              "headline-lg": ["\"Source Serif 4\""],
              "headline-md": ["\"Source Serif 4\""],
              "display-lg": ["\"Source Serif 4\""],
              "body-lg": ["Hanken Grotesk"],
              "headline-lg-mobile": ["\"Source Serif 4\""]
          },
          "fontSize": {
              "body-md": ["16px", { "lineHeight": "24px", "fontWeight": "400" }],
              "label-sm": ["12px", { "lineHeight": "16px", "fontWeight": "500" }],
              "label-md": ["14px", { "lineHeight": "20px", "letterSpacing": "0.05em", "fontWeight": "600" }],
              "headline-lg": ["32px", { "lineHeight": "40px", "letterSpacing": "-0.01em", "fontWeight": "600" }],
              "headline-md": ["24px", { "lineHeight": "32px", "fontWeight": "600" }],
              "display-lg": ["48px", { "lineHeight": "56px", "letterSpacing": "-0.02em", "fontWeight": "700" }],
              "body-lg": ["18px", { "lineHeight": "28px", "fontWeight": "400" }],
              "headline-lg-mobile": ["28px", { "lineHeight": "36px", "fontWeight": "600" }]
          }
      }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries')
  ],
}
