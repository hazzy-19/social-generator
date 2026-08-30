---
name: The Quiet Authority
colors:
  surface: '#f9f9ff'
  surface-dim: '#d9dadf'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f9'
  surface-container: '#ededf3'
  surface-container-high: '#e7e8ee'
  surface-container-highest: '#e2e2e8'
  on-surface: '#191c20'
  on-surface-variant: '#414848'
  inverse-surface: '#2e3035'
  inverse-on-surface: '#f0f0f6'
  outline: '#717878'
  outline-variant: '#c1c8c8'
  surface-tint: '#436465'
  primary: '#000d0d'
  on-primary: '#ffffff'
  primary-container: '#002627'
  on-primary-container: '#6d8f90'
  inverse-primary: '#aacdce'
  secondary: '#4b6264'
  on-secondary: '#ffffff'
  secondary-container: '#cbe4e6'
  on-secondary-container: '#506769'
  tertiary: '#030c0d'
  on-tertiary: '#ffffff'
  tertiary-container: '#182324'
  on-tertiary-container: '#7f8b8c'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c5e9ea'
  primary-fixed-dim: '#aacdce'
  on-primary-fixed: '#002021'
  on-primary-fixed-variant: '#2b4c4d'
  secondary-fixed: '#cee7e9'
  secondary-fixed-dim: '#b2cbcd'
  on-secondary-fixed: '#071f21'
  on-secondary-fixed-variant: '#344b4d'
  tertiary-fixed: '#d9e5e6'
  tertiary-fixed-dim: '#bdc9ca'
  on-tertiary-fixed: '#131d1e'
  on-tertiary-fixed-variant: '#3e494a'
  background: '#f9f9ff'
  on-background: '#191c20'
  surface-variant: '#e2e2e8'
typography:
  display-lg:
    fontFamily: Source Serif 4
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Source Serif 4
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Source Serif 4
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-md:
    fontFamily: Source Serif 4
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Hanken Grotesk
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 20px
  container-max: 1120px
---

## Brand & Style

The design system is built upon the concept of **Editorial Precision**. It targets an intellectually curious audience that values substance over flash. The UI evokes an emotional response of focused calm, reliability, and timelessness. 

The design style is a blend of **Modern Minimalism** and **Classical Editorial**. It utilizes generous whitespace to create a "breathing" canvas, allowing content to take center stage. Visual noise is aggressively reduced, favoring thin strokes and structural alignment over decorative elements. The result is a UI that feels like a premium printed journal—authoritative, quiet, and intentional.

## Colors

The palette is restricted to maintain a high-contrast, professional atmosphere. 

- **Primary (#002627):** A deep forest green used for headlines, primary actions, and brand-heavy moments. It provides the "authority."
- **Surface (#F9F9FF):** An off-white, cool-toned neutral that reduces eye strain compared to pure white, serving as the primary background.
- **Secondary:** Muted variants of the forest green used for secondary text and supporting icons.
- **Accent:** A deep oxblood red is reserved exclusively for critical alerts or "editorial highlights" to maintain a sophisticated tone.

Avoid gradients. All color applications must be solid and purposeful.

## Typography

Typography is the cornerstone of this design system. We pair the authoritative, bookish nature of **Source Serif 4** with the clean, contemporary precision of **Hanken Grotesk**.

- **Headlines:** Always use Source Serif 4. For large displays, use a tighter letter-spacing to emphasize the editorial feel.
- **Body:** Hanken Grotesk provides high legibility for long-form reading. Ensure line heights are generous (1.5x minimum) to maintain the "quiet" aesthetic.
- **Labels:** Use Hanken Grotesk in Medium or SemiBold weights. Small labels should occasionally use uppercase with slight tracking to differentiate them from body text without changing size.

## Layout & Spacing

The layout follows a **Fixed Grid** philosophy on desktop to mimic the structured columns of a premium broadsheet. 

- **Grid:** A 12-column system for desktop, 6-column for tablet, and 4-column for mobile.
- **Rhythm:** All spacing must be multiples of 4px. Use larger gaps (48px+) between major sections to enforce a feeling of prestige and "slow" consumption.
- **Alignment:** Content is typically left-aligned to mirror reading patterns. Minimal use of centered text, reserved only for splash moments or pull-quotes.

## Elevation & Depth

This design system eschews shadows in favor of **Tonal Layers** and **1px Dividers**. 

- **Depth:** Create hierarchy by placing elements on slightly different tinted surfaces (e.g., a card using a slightly darker neutral than the background).
- **Dividers:** Use 1px solid lines in a light gray (#E0E0E0) or the primary color at 10% opacity. Dividers should be used to separate logical sections rather than boxing everything in.
- **Interaction:** State changes (hover/active) should be communicated via subtle color shifts or underline transitions rather than elevation increases.

## Shapes

The shape language is disciplined and geometric. 

- **Standard Elements:** Buttons and input fields use a **4px (0.25rem)** corner radius, providing a hint of softness while maintaining a crisp, architectural silhouette.
- **Pills/Chips:** Specific navigational elements like hashtags and primary buttons use a fully rounded (pill) shape to provide a clear interactive affordance that contrasts against the rectangular grid.
- **Images:** Photography should always have sharp (0px) corners to preserve the editorial look.

## Components

- **Buttons:** Primary buttons are pill-shaped, filled with the Primary color, and use white Hanken Grotesk text. Secondary buttons are ghost-style with a 1px Primary color border.
- **Tab Toggles:** Use a "Segmented Control" style. A subtle light-gray container with a sliding 4px rounded white background indicates the active selection. 
- **Chip-style Hashtags:** Small, pill-shaped elements with a very light tint of the primary color and dark text. No borders for chips; use background fills only.
- **Input Fields:** 1px solid borders on all four sides. On focus, the border weight remains 1px but shifts to the Primary color. No shadows.
- **Cards:** Cards are defined by 1px borders or subtle background shifts. Avoid heavy containerization; let the typography and white space define the boundaries of the content.
- **Lists:** Use 1px horizontal dividers between items. Ensure vertical padding within list items is at least 16px to maintain the spacious aesthetic.