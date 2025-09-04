# Budget Buddy Mobile

React Native mobile app built with Expo for Budget Buddy - an offline-first budget calculator and savings tracker.

## Features

- **Offline-first**: Works without internet connection using local SQLite database
- **Budget Calculator**: Calculate budget breakdown with customizable time periods (daily/weekly/monthly)
- **Savings Forecast**: Project savings growth with compound interest
- **AI Insights**: Smart recommendations and financial health scoring
- **Data Sync**: Automatic sync with FastAPI backend when online
- **Cross-platform**: Works on both iOS and Android

## Tech Stack

- **React Native** with Expo
- **TypeScript** for type safety
- **Zustand** for state management
- **Expo SQLite** for offline storage
- **React Query** for data fetching and caching
- **AsyncStorage** for app state persistence

## Project Structure

```
mobile/
├── app/                    # Expo Router app directory
│   ├── _layout.tsx         # Root layout with providers
│   └── (tabs)/            # Tab navigation
│       ├── _layout.tsx    # Tab layout
│       └── dashboard.tsx  # Budget calculator screen
├── components/            # Reusable UI components
│   └── BudgetChart.tsx   # Budget visualization
├── services/             # API and database services
│   ├── budgetService.ts  # Budget calculations (online/offline)
│   └── databaseService.ts # SQLite operations
├── stores/               # State management
│   └── budgetStore.ts    # Budget state with Zustand
├── package.json          # Dependencies and scripts
└── app.json             # Expo configuration
```

## Setup Instructions

1. **Install dependencies**:
   ```bash
   cd mobile
   npm install
   ```

2. **Start development server**:
   ```bash
   npx expo start
   ```

3. **Run on device/simulator**:
   - Scan QR code with Expo Go app (Android)
   - Scan QR code with Camera app (iOS)
   - Press 'i' for iOS simulator
   - Press 'a' for Android emulator

## Backend Integration

The mobile app connects to the FastAPI backend at `http://localhost:8000` for:

- Budget calculations (when online)
- Savings forecasts
- AI insights
- Data synchronization

When offline, the app uses local business logic that mirrors the backend calculations.

## Development Notes

- **State Management**: Uses Zustand with persistence via AsyncStorage
- **Database**: Local SQLite database mirrors backend schema
- **Sync Strategy**: Queue-based sync with retry logic
- **Error Handling**: Graceful fallbacks for offline scenarios
- **Type Safety**: Full TypeScript coverage with proper interfaces

## Key Components

### BudgetStore
- Manages global app state
- Handles online/offline calculations
- Persists data to AsyncStorage
- Queues operations for sync

### BudgetService
- API client for FastAPI backend
- Offline calculation methods
- Mirrors backend business logic

### DatabaseService
- SQLite database operations
- Sync queue management
- Local data persistence

### BudgetChart
- Visual budget breakdown
- Progress bars and percentages
- Responsive design for mobile

## Building for Production

```bash
# Build for iOS
npx expo build:ios

# Build for Android
npx expo build:android

# Or use EAS Build (recommended)
eas build --platform all
```
