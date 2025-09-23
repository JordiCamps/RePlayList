# RePlayList Frontend

A modern SvelteKit application for transferring playlists between Spotify and YouTube platforms.

## Architecture

### Technology Stack
- **Framework**: SvelteKit with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Svelte stores with composable patterns
- **Icons**: Lucide Svelte
- **Build Tool**: Vite
- **Package Manager**: npm

### Project Structure

```
src/
├── lib/
│   ├── api/                 # API client modules
│   │   ├── auth.ts         # Authentication endpoints
│   │   ├── config.ts       # Configuration endpoints
│   │   ├── playlists.ts    # Playlist management
│   │   └── transfer.ts     # Transfer operations
│   ├── components/         # Reusable UI components
│   │   ├── LoadingOverlay.svelte
│   │   ├── Navigation.svelte
│   │   ├── NotificationSystem.svelte
│   │   ├── PlaylistCard.svelte
│   │   ├── ProgressBar.svelte
│   │   ├── SourceSelector.svelte
│   │   ├── StepNav.svelte
│   │   ├── Stepper.svelte
│   │   ├── TargetSelector.svelte
│   │   ├── ThemeToggle.svelte
│   │   ├── Tooltip.svelte
│   │   └── TransferSummary.svelte
│   ├── composables/        # Reusable logic functions
│   │   ├── useAccessibility.ts
│   │   ├── useAnimations.ts
│   │   ├── useDebounce.ts
│   │   ├── useErrorHandling.ts
│   │   ├── useLazyLoad.ts
│   │   ├── useLoadingStates.ts
│   │   ├── useMemo.ts
│   │   └── useResponsive.ts
│   ├── services/           # Business logic layer
│   │   ├── authService.ts
│   │   ├── playlistService.ts
│   │   └── transferService.ts
│   ├── stores/             # State management
│   │   ├── authStore.ts
│   │   ├── playlistStore.ts
│   │   ├── themeStore.ts
│   │   ├── transferStore.ts
│   │   └── uiStore.ts
│   └── types/              # TypeScript definitions
│       └── ui.ts
└── routes/
    ├── components/
    │   └── TransferWizard.svelte  # Main application orchestrator
    ├── steps/              # Step-based UI components
    │   ├── CompleteStep.svelte
    │   ├── ConfirmationStep.svelte
    │   ├── ConnectionStep.svelte
    │   ├── DirectionStep.svelte
    │   ├── ProgressStep.svelte
    │   └── SelectionStep.svelte
    ├── auth-callback/
    │   └── +page.svelte    # OAuth callback handler
    ├── +layout.svelte      # Root layout
    ├── +layout.ts          # Layout configuration
    └── +page.svelte        # Main page (6 lines)
```

## Development

### Prerequisites
- Node.js 18+ 
- npm 9+

### Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run check
```

### Environment Variables
Create `.env.local` for local development:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=RePlayList
```

## State Management

### Store Architecture
The application uses a modular store pattern with clear separation of concerns:

- **`authStore`**: Authentication state and user tokens
- **`playlistStore`**: Playlist data and filtering
- **`transferStore`**: Transfer workflow and progress
- **`uiStore`**: UI state, notifications, and modals
- **`themeStore`**: Theme and appearance settings

### Composable Pattern
Reusable logic is encapsulated in composables:
- **`useDebounce`**: Input debouncing for search
- **`useMemo`**: Memoization for expensive computations
- **`useLazyLoad`**: Lazy loading for components and data
- **`useAccessibility`**: ARIA labels and keyboard navigation
- **`useAnimations`**: Animation presets and transitions
- **`useResponsive`**: Screen size detection and breakpoints
- **`useErrorHandling`**: Error management and recovery
- **`useLoadingStates`**: Loading state management

## Component Architecture

### Design Principles
- **Single Responsibility**: Each component has one clear purpose
- **Composition over Inheritance**: Components are composed together
- **Props Down, Events Up**: Clear data flow patterns
- **Accessibility First**: WCAG 2.1 AA compliance
- **Performance Optimized**: Lazy loading and memoization

### Component Categories

#### Layout Components
- **`TransferWizard`**: Main application orchestrator
- **`Navigation`**: Top navigation with theme toggle
- **`StepNav`**: Step navigation component

#### Form Components
- **`SourceSelector`**: Source playlist selection with search
- **`TargetSelector`**: Target playlist selection
- **`ConnectionStep`**: Platform authentication

#### Feedback Components
- **`ProgressBar`**: Animated progress visualization
- **`LoadingOverlay`**: Modal loading screen
- **`NotificationSystem`**: Toast notifications
- **`TransferSummary`**: Transfer results display

#### Utility Components
- **`PlaylistCard`**: Playlist display card
- **`Stepper`**: Step indicator
- **`ThemeToggle`**: Dark/light mode toggle
- **`Tooltip`**: Contextual help tooltips

## API Integration

### Client Architecture
API clients are organized by domain:
- **`auth.ts`**: Authentication and token management
- **`playlists.ts`**: Playlist CRUD operations
- **`transfer.ts`**: Transfer initiation and monitoring
- **`config.ts`**: Application configuration

### Error Handling
Comprehensive error handling with:
- HTTP status code mapping
- Retry logic with exponential backoff
- User-friendly error messages
- Recovery action suggestions

### Loading States
Granular loading state management:
- Per-operation loading indicators
- Progress tracking with time estimation
- Cancellation support
- Visual feedback

## Styling

### Design System
- **Tailwind CSS**: Utility-first styling
- **Custom CSS**: Component-specific styles in `app.css`
- **Dark Mode**: System preference detection
- **Responsive**: Mobile-first approach

### Theme Configuration
```css
:root {
  --color-primary: #3b82f6;
  --color-secondary: #6366f1;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
}
```

## Performance

### Optimizations
- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Components and data loaded on demand
- **Memoization**: Expensive computations cached
- **Debouncing**: Search input optimization (300ms)
- **Image Optimization**: Lazy loading and responsive images

### Bundle Analysis
```bash
npm run build
# Check dist/ folder for bundle analysis
```

## Accessibility

### Implementation
- **ARIA Labels**: Comprehensive labeling
- **Keyboard Navigation**: Full keyboard support
- **Focus Management**: Proper focus handling
- **Screen Reader**: Live regions and announcements
- **Color Contrast**: WCAG AA compliance

### Testing
```bash
# Run accessibility checks
npm run check
```

## Testing

### Type Checking
```bash
npm run check
```

### Manual Testing
- Cross-browser compatibility
- Responsive design validation
- Accessibility testing
- Performance profiling

## Build and Deployment

### Production Build
```bash
npm run build
```

### Environment Configuration
- Development: `npm run dev`
- Production: `npm run build && npm run preview`

### Deployment Considerations
- Static site generation support
- Environment variable configuration
- CDN optimization
- Caching strategies

## Troubleshooting

### Common Issues

#### TypeScript Errors
```bash
npm run check
```

#### Build Failures
- Check Node.js version compatibility
- Clear `node_modules` and reinstall
- Verify environment variables

#### Runtime Errors
- Check browser console for errors
- Verify API connectivity
- Check authentication state

### Debug Mode
Enable debug logging in development:
```javascript
// In browser console
localStorage.setItem('debug', 'true')
```

## Contributing

### Code Style
- Follow existing patterns
- Use TypeScript strict mode
- Implement proper error handling
- Add accessibility attributes
- Write self-documenting code

### Component Guidelines
- Single responsibility principle
- Props interface definition
- Event dispatching
- Accessibility compliance
- Performance optimization

### State Management
- Use appropriate store for data
- Implement proper actions
- Handle loading and error states
- Maintain data consistency

## Dependencies

### Core Dependencies
- `svelte`: ^4.2.0
- `sveltekit`: ^2.0.0
- `typescript`: ^5.0.0
- `tailwindcss`: ^3.4.0

### Development Dependencies
- `@sveltejs/adapter-auto`: ^3.0.0
- `@sveltejs/kit`: ^2.0.0
- `@typescript-eslint/eslint-plugin`: ^7.0.0
- `@typescript-eslint/parser`: ^7.0.0
- `eslint`: ^8.57.0
- `eslint-config-prettier`: ^9.1.0
- `eslint-plugin-svelte`: ^2.44.0
- `prettier`: ^3.2.0
- `prettier-plugin-svelte`: ^3.2.0
- `svelte-check`: ^3.6.0
- `tslib`: ^2.6.0
- `vite`: ^5.2.0

### Runtime Dependencies
- `lucide-svelte`: ^0.400.0