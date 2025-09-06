# APK Build & AI Setup Guide

## 🚀 Building Budget Buddy Mobile APK

### Prerequisites
- Node.js 18+ installed
- Expo CLI installed (`npm install -g @expo/cli`)
- Grok API Key (optional, for AI features)

### Step 1: Install Dependencies
```bash
cd mobile
npm install
```

### Step 2: Configure AI Features (Optional)
Create `.env.local` file in the mobile directory:
```bash
# For AI-powered insights
EXPO_PUBLIC_GROK_API_KEY=your-grok-api-key-here
```

**Get Grok API Key:**
1. Visit: https://console.x.ai/
2. Sign up/login to X.AI Console
3. Create new API key
4. Copy the key to your .env.local file

### Step 3: Build APK

#### Option A: EAS Build (Recommended - Cloud Build)
```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo account (create free account if needed)
eas login

# Configure build
eas build:configure

# Build Android APK
eas build --platform android --profile preview
```

#### Option B: Local Build (Requires Android Studio)
```bash
# Create development build
npx expo run:android

# Or create standalone APK
npx expo build:android
```

### Step 4: Install on Device
1. Download the APK from EAS build dashboard or local build
2. Enable "Install from Unknown Sources" on your Android device
3. Transfer APK to device and install
4. Launch "Budget Buddy" app

## 📱 Features Available in APK

### With Internet Connection:
✅ **Full Grok AI Integration**
- Real-time financial insights
- AI-powered budget recommendations  
- Personalized spending analysis
- Philippine financial news updates
- Smart budget categorization

### Offline Mode:
✅ **Core Functionality**
- Bills management (add/edit/archive/delete)
- Budget calculations and breakdowns
- User profile and settings
- Data persistence (SQLite database)
- Full UI navigation

### Data Storage:
- **SQLite Database**: All data stored locally on device
- **Persistent Storage**: Data survives app restarts
- **No Cloud Dependency**: Core features work without internet
- **Privacy**: Your financial data stays on your device

## 🔧 Development Testing

### Live Reload for Testing:
```bash
# Start development server
npx expo start

# Scan QR code with Expo Go app for live testing
# Changes reflect immediately without rebuilding APK
```

### Production APK Testing:
- Install APK on device for production-like testing
- Test offline functionality by disabling internet
- Verify AI features work with internet connection
- All data persists between app launches

## 🎯 Result

You'll have a fully functional Budget Buddy app on your device that:
- Works entirely offline for core features
- Enhances with AI when internet is available
- Stores all data locally on your device
- Provides continuous testing capabilities
- Maintains professional logging and error handling
