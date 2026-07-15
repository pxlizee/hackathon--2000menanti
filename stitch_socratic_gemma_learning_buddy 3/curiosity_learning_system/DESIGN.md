---
name: Curiosity Learning System
colors:
  surface: '#faf9f5'
  surface-dim: '#dbdad6'
  surface-bright: '#faf9f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f4f0'
  surface-container: '#efeeea'
  surface-container-high: '#e9e8e4'
  surface-container-highest: '#e3e2df'
  on-surface: '#1b1c1a'
  on-surface-variant: '#564338'
  inverse-surface: '#2f312e'
  inverse-on-surface: '#f2f1ed'
  outline: '#8a7266'
  outline-variant: '#ddc1b3'
  surface-tint: '#9a4600'
  primary: '#9a4600'
  on-primary: '#ffffff'
  primary-container: '#ff8a3d'
  on-primary-container: '#682d00'
  inverse-primary: '#ffb68d'
  secondary: '#0060ac'
  on-secondary: '#ffffff'
  secondary-container: '#68abff'
  on-secondary-container: '#003e73'
  tertiary: '#006d41'
  on-tertiary: '#ffffff'
  tertiary-container: '#5cbc86'
  on-tertiary-container: '#00482a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdbc9'
  primary-fixed-dim: '#ffb68d'
  on-primary-fixed: '#321200'
  on-primary-fixed-variant: '#763300'
  secondary-fixed: '#d4e3ff'
  secondary-fixed-dim: '#a4c9ff'
  on-secondary-fixed: '#001c39'
  on-secondary-fixed-variant: '#004883'
  tertiary-fixed: '#95f7bb'
  tertiary-fixed-dim: '#7adaa1'
  on-tertiary-fixed: '#002110'
  on-tertiary-fixed-variant: '#005230'
  background: '#faf9f5'
  on-background: '#1b1c1a'
  surface-variant: '#e3e2df'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Be Vietnam Pro
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Be Vietnam Pro
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Be Vietnam Pro
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
---

## Brand & Style

This design system is built on the principles of **Joyful Discovery** and **Gentle Guidance**. It is specifically tailored for a child-friendly learning environment, balancing high energy with a sense of safety and structured progress. The aesthetic is a blend of **Modern-Tactile** and **Organic Minimalism**, utilizing soft shapes and vibrant accents to create an inviting digital playground.

The visual narrative focuses on:
- **Approachability:** Every interface element feels touchable and safe, avoiding sharp corners or intimidating densities.
- **Optimism:** A high-vibrancy color palette that stimulates engagement without overwhelming the senses.
- **Clarity:** Information architecture is simplified to reduce cognitive load for younger learners, using clear iconography and generous negative space.
- **Encouragement:** Subtle animations and "squishy" interactions provide positive reinforcement during the learning journey.

## Colors

The palette is designed to be "vibrant-pastel"—saturated enough to be playful, but tempered with white values to keep it soft on the eyes for extended study sessions.

- **Primary (Sunset Orange):** Used for primary actions, progress indicators, and celebratory moments. It evokes energy and warmth.
- **Secondary (Sky Blue):** Used for navigation elements, supportive information, and focus states. It provides a calming counterpoint to the primary orange.
- **Tertiary (Leaf Green):** Dedicated to success states, "Correct" answers, and growth-related metrics.
- **Neutral (Cream White):** Instead of pure white, a soft cream base is used to reduce screen glare and provide a more "paper-like" organic feel.
- **Accents:** Muted versions of these colors should be used for background containers to maintain hierarchy without adding visual noise.

## Typography

The typography strategy prioritizes high x-heights and open counters to ensure maximum legibility for developing readers.

- **Headlines:** **Plus Jakarta Sans** is used for its geometric yet soft personality. The bold and extra-bold weights provide clear signposting and a modern, friendly character.
- **Body & Labels:** **Be Vietnam Pro** offers a contemporary, clean look that remains legible at smaller sizes. Its slightly wider character set feels airy and non-threatening.
- **Scale:** Larger-than-average body text (18px for primary content) is utilized to accommodate varying reading levels and touch-target accessibility.

## Layout & Spacing

This design system employs a **Fluid-Fixed Hybrid** model. While content containers have a maximum width on desktop to prevent eye-strain, internal components use a fluid 12-column grid.

- **Rhythm:** An 8px base unit ensures consistent scaling. Larger gaps (48px+) are encouraged between distinct learning modules to prevent "clutter-induced" anxiety.
- **Mobile:** Margins shrink to 16px, and multi-column layouts reflow into a single-column stacked view.
- **Safe Areas:** Interactive elements must maintain a minimum 44px hit-zone, padded with at least 'sm' spacing from adjacent interactive components.

## Elevation & Depth

To maintain the "friendly" and "tactile" feel, depth is created through **Tonal Stacking** and **Soft Ambient Shadows**.

- **Surface Tiers:** Backgrounds use the Neutral base. Content cards sit on a pure white surface. Interactive elements (like buttons) use high-saturation colors to "pop."
- **Shadows:** Use large blur radii (16px+) with very low opacity (5-8%). Tint shadows with the brand's secondary blue rather than pure black to keep the UI looking "clean" and vibrant.
- **Interaction Depth:** On hover or press, components should use a slight "inner shadow" or "y-axis shift" to mimic a physical button being pressed into a soft surface.

## Shapes

The shape language is strictly **Rounded**. 

- **Standard Radius:** 0.5rem (8px) is the minimum for any functional element. 
- **Large Radius:** 1rem (16px) is preferred for containers and cards to emphasize the welcoming nature of the platform.
- **Decorative Shapes:** Abstract blobs and "scalloped" edges (inspired by the reference images) should be used as background dividers to break the monotony of straight horizontal lines.

## Components

### Buttons
Buttons are the primary vehicle for playfulness.
- **Primary:** Filled Sunset Orange with a subtle "thick" bottom border (2px darker shade) to create a 3D effect.
- **Secondary:** Sky Blue with a white outline.
- **Shape:** Highly rounded (pill-shaped for smaller buttons, 12px radius for large action buttons).

### Cards
- **Structure:** White background, 16px corner radius, soft blue-tinted shadow.
- **Headers:** Often feature a solid colored top-bar or icon "sticker" that breaks the top boundary for a whimsical look.

### Input Fields
- **Styling:** Extra thick borders (2px) in a light grey or soft blue.
- **Focus:** When active, the border turns Secondary Blue and the shadow increases in intensity to draw the student's eye.

### Chips & Badges
- **Usage:** For categorization (e.g., "Math," "Science").
- **Style:** Low-saturation versions of the primary/secondary colors with high-saturation text to ensure legibility without being distracting.

### Lists
- Lists should replace standard bullets with custom icons (e.g., small stars, leaves, or colored dots) to reinforce the educational theme.