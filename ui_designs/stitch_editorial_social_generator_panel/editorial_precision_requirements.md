# Editorial Precision: Design & Functional Requirements

This document formalizes the visual identity and functional constraints for "The Quiet Authority" project, specifically the Social Generator utility.

## 🎨 Visual Identity (Editorial Precision)

### Brand Personality
*   **Minimalist & Focused**: A quiet, authoritative aesthetic that prioritizes content and clarity over decorative elements.
*   **Editorial Professionalism**: Inspired by high-end typography and clean print layouts.

### Color Palette
*   **Primary Accent**: `#002627` (Deep Forest Green) — Used for primary buttons, active states, and key icons.
*   **Surface (Base)**: `#f9f9ff` (Off-White) — Used for cards, panels, and input backgrounds.
*   **Background (Muted)**: `#f4f4fb` (Soft Muted Blue) — Used for the page viewport in standalone tool views to create focus.
*   **Borders/Dividers**: 1px width, muted contrast (Surface-Dim) to maintain structure without noise.
*   **No Purple**: Explicit constraint to avoid the standard UI "accent" palettes in favor of the custom forest green.

### Typography
*   **Headlines**: *Source Serif 4* — Used for titles, section headers, and the wordmark to provide an authoritative editorial feel.
*   **Body & Labels**: *Hanken Grotesk* — A clean, modern sans-serif used for readability in captions, labels, and secondary text.

### Geometry & Styling
*   **Corner Radius**: `4px` (Round Four) — Applied to buttons, cards, inputs, and image previews for a refined, slightly softened look.
*   **Elevation**: No heavy shadows; depth is communicated through subtle background shifts and thin borders.

---

## 🛠 Functional Requirements

### Social Generator Component
*   **Dynamic Inputs**: 
    *   **Source Content**: A plain textarea for raw text input or notes.
    *   **Caption Textarea**: Must be **auto-growing** so all text remains fully visible without clipping or scrollbars within the element.
*   **Platform Context**: Support for Instagram, LinkedIn, X (Twitter), and Facebook via tabbed navigation.
*   **Content Indicators**: 
    *   **Character Counters**: Must sit on a dedicated line below the caption text, right-aligned, clearly separated from the input field.
    *   **Hashtag Pills**: Grouped below the counter for easy scanning.
*   **Hierarchical Actions**:
    1.  **Primary**: "Copy Caption" — Solid `#002627` background with bold white text. Must read as clearly active/clickable.
    2.  **Secondary**: "Image" and "Save" — Outlined buttons with icons, placed side-by-side.

### Layout & Responsiveness
*   **Desktop Two-Column**: For large screens, the generator uses a balanced 900px centered card with a horizontal split (Image Preview left, Refinement Tools right).
*   **Mobile/Tablet**: Transitions to a vertical stack for ergonomic use on narrow screens, ensuring the "Input → Preview → Action" flow remains intuitive.
*   **Standalone Utility**: Designed as a private, distraction-free tool without global site navigation or blog footers.
