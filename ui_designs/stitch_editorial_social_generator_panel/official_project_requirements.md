# Official Requirements: The Quiet Authority & Social Generator

This document serves as the formal specification for "The Quiet Authority" project, codifying the visual identity and functional requirements for the Social Generator utility.

## 🎨 Visual Identity (Editorial Precision)

### Brand Personality
*   **Minimalist & Focused**: A quiet, authoritative aesthetic that prioritizes content and clarity over decorative elements.
*   **Editorial Professionalism**: Inspired by high-end typography and clean print layouts.

### Color Palette
*   **Primary Accent**: `#002627` (Deep Forest Green) — Used for primary buttons, active navigation states, and key icons.
*   **Surface (Base)**: `#f9f9ff` (Off-White) — Used for cards, panels, and input backgrounds.
*   **Background (Muted)**: `#f4f4fb` (Soft Muted Blue) — Used for the page viewport in standalone views to create depth and focus.
*   **Borders/Dividers**: 1px width, muted contrast (Surface-Dim) to maintain structure without visual noise.
*   **Constraint**: No purple or standard UI "neon" accents; stick to the forest green and muted palette.

### Typography
*   **Headlines**: *Source Serif 4* — Used for titles, section headers, and the wordmark for an authoritative editorial feel.
*   **Body & Labels**: *Hanken Grotesk* (or clean sans-serif equivalent) — Used for readability in captions, labels, and secondary text.

### Geometry & Styling
*   **Corner Radius**: `4px` (Round Four) — Applied to buttons, cards, inputs, and image previews.
*   **Elevation**: No heavy shadows; depth is communicated through subtle background shifts and 1px borders.

---

## 🛠 Functional Requirements

### Social Generator Component
*   **Dynamic Inputs**: 
    *   **Source Content**: A plain textarea for raw text input or notes.
    *   **Caption Textarea**: Auto-growing height to ensure all generated text is visible without internal scrollbars.
*   **Platform Context**: Support for Instagram, LinkedIn, X (Twitter), and Facebook via tabbed navigation.
*   **Content Indicators**: 
    *   **Character Counters**: Platform-aware (e.g., 2200 for Instagram, 280 for X). Displays warning states (amber/red) when nearing limits.
    *   **Hashtag Pills**: Grouped below the counter for easy scanning and removal.
*   **Granular Approval**: Independent "Approve" (check icon) and "Reload" (circular arrow) controls for the Image, Caption, and Hashtag sections.
*   **Actions**:
    1.  **Primary**: "Copy Caption" — Solid `#002627` background, bold white text.
    2.  **Secondary**: "Image" and "Save" — Outlined buttons placed side-by-side.

### Navigation & Architecture
*   **Global Navigation**: A clean top bar containing "Generator", "History", and "Library". Active states marked with a bottom-border accent.
*   **Dedicated History**: A separate view for "Past Generations" featuring search, platform filtering, and "Restore" capabilities.

### Layout & Responsiveness
*   **Desktop Two-Column**: Horizontal split for the generator (Image Preview left, Refinement Tools right) within a 900px centered card.
*   **Mobile**: Vertical stack (Input → Preview → Action) for ergonomic use on narrow screens.
*   **Standalone Utility**: Designed to function independently of the main blog dashboard when needed.