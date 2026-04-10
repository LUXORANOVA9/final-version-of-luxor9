# Design System Reference

## Color Tokens

### Primary (Cyan)
```
--color-primary-50: #e6f9ff
--color-primary-100: #b3eaff
--color-primary-200: #80dbff
--color-primary-300: #4dcbff
--color-primary-400: #26bdff
--color-primary-500: #00d4ff (DEFAULT)
--color-primary-600: #00a8cc
--color-primary-700: #007d99
--color-primary-800: #005266
--color-primary-900: #002633
```

### Secondary (Purple)
```
--color-secondary-500: #8b5cf6 (DEFAULT)
```

### Semantic Colors
```
--color-accent-success: #10b981
--color-accent-warning: #f59e0b
--color-accent-error: #ef4444
--color-accent-info: #3b82f6
```

## Typography

### Font Stack
```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

### Type Scale
| Name | Size | Weight | Use |
|------|------|--------|-----|
| Display | 72px | 800 | Hero headlines |
| H1 | 48px | 800 | Page titles |
| H2 | 36px | 700 | Section titles |
| H3 | 24px | 700 | Card titles |
| H4 | 20px | 600 | Subsections |
| Body | 16px | 400 | Body text |
| Body SM | 14px | 400 | Small text |
| Caption | 12px | 500 | Labels |

## Spacing

4px base unit:
- `space-1`: 4px
- `space-2`: 8px
- `space-3`: 12px
- `space-4`: 16px
- `space-6`: 24px
- `space-8`: 32px
- `space-12`: 48px
- `space-16`: 64px

## Border Radius

```
radius-sm: 4px
radius-md: 8px (default)
radius-lg: 12px
radius-xl: 16px
radius-2xl: 24px
radius-full: 9999px (pills)
```

## Shadows

```
shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05)
shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1)
shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1)
shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1)
shadow-glow-primary: 0 0 20px rgba(0, 212, 255, 0.3)
shadow-glow-secondary: 0 0 20px rgba(139, 92, 246, 0.3)
```

## Animations

```
animate-fade-in: 300ms ease-out
animate-slide-up: 400ms cubic-bezier(0.16, 1, 0.3, 1)
animate-scale-in: 200ms cubic-bezier(0.34, 1.56, 0.64, 1)
animate-pulse-glow: 2s infinite
animate-float: 6s ease-in-out infinite
```

## Components

### Button
Variants: `default`, `secondary`, `outline`, `ghost`, `link`, `success`
Sizes: `sm`, `default`, `lg`, `xl`, `icon`

### Card
Full card system with Header, Title, Description, Content, Footer

### Badge
Variants: `default`, `secondary`, `success`, `warning`, `error`, `info`, `outline`

### Input
Standard input with focus ring

## Usage

```tsx
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export function Example() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Hello World</CardTitle>
      </CardHeader>
      <CardContent>
        <Button variant="default">Click me</Button>
      </CardContent>
    </Card>
  );
}
```
