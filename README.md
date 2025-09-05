# Budget Buddy Mobile

**🚀 Production-Ready** - An AI-powered mobile budget calculator and financial management app built with React Native and Expo.

## ✨ Features

### Core Functionality
- **Smart Budget Calculations**: Input any budget amount with instant Filipino-context breakdowns
- **Bills Management**: Add, edit, archive, and delete recurring bills with intuitive UI
- **AI-Powered Insights**: Grok AI integration for personalized financial advice
- **Offline-First Design**: Works seamlessly without internet connection
- **Philippine Context**: Tailored recommendations for Filipino lifestyle and economy

### Technical Highlights
- **React Native + Expo**: Cross-platform mobile development
- **Zustand State Management**: Efficient and scalable state handling
- **SQLite Database**: Local data persistence and offline capabilities
- **Professional Logging**: Production-ready logging system with structured output
- **MIT Licensed**: Open source with comprehensive documentation

## 🔧 Technical Stack

### Frontend (Mobile)
- **React Native** with Expo SDK 51
- **TypeScript** for type safety
- **Zustand** for state management
- **SQLite** for local database
- **React Navigation** for screen routing

### Backend Services
- **Python FastAPI** for API services
- **SQLite** for data persistence  
- **Grok AI** for intelligent financial insights
- **Authentication** with secure session management

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Expo CLI** (`npm install -g @expo/cli`)
- **Python** 3.11+ (for backend services)
- **Grok API Key** (optional, for AI features)

## 🚀 Quick Start

### Mobile App Setup

1. **Clone the repository:**
```bash
git clone https://github.com/jekportillano-da/Project-Adam-20-1.git
cd Project-Adam-20-1/mobile
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure environment (optional for AI features):**
```bash
# Create .env.local file
echo "EXPO_PUBLIC_GROK_API_KEY=your-grok-api-key" > .env.local
```

4. **Start the development server:**
```bash
npx expo start
```

5. **Run on device:**
- Install Expo Go app on your phone
- Scan the QR code from the terminal
- Or use Android/iOS simulator

### Backend Services (Optional)

1. **Setup Python environment:**
```bash
cd .. # Back to project root
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Start backend services:**
```bash
# Development mode
python main_dev.py

# Production mode  
python main_prod.py
```

## 📱 Usage

### Core Features
1. **Budget Calculator**: Enter your budget amount and select timeframe
2. **Bills Management**: Add recurring bills with amounts and due dates
3. **AI Insights**: Get personalized financial recommendations (requires API key)
4. **Offline Mode**: All features work without internet connection

### Navigation
- **Dashboard**: Budget overview and quick actions
- **Bills**: Manage recurring expenses with archive/delete
- **Insights**: AI-powered financial analysis and news
- **Profile**: User settings and preferences

## 🔧 Configuration

### Environment Variables
```bash
# .env.local (for mobile app)
EXPO_PUBLIC_GROK_API_KEY=your-grok-api-key-here

# Backend (if using API services)
GROK_API_KEY=your-grok-api-key-here
```

### Database
- **SQLite** database automatically created on first run
- **Offline-first** design with sync capabilities
- **Data persistence** across app restarts

## 📊 Project Structure

```
Budget Buddy Mobile/
├── mobile/                 # React Native mobile app
│   ├── app/(tabs)/        # Main app screens
│   ├── stores/            # Zustand state management
│   ├── services/          # Business logic & API calls
│   ├── components/        # Reusable UI components
│   └── utils/             # Logging and utilities
├── auth/                  # Authentication services
├── common/                # Shared backend utilities
├── goals/                 # Goals tracking system
└── docs/                  # Documentation
```

## Development

- Flask routes are in `app/routes.py`
- DeepSeek integration is in `app/services/generator.py`
- Frontend templates are in `app/templates/`
- Static files (CSS, JS) are in `app/static/`

## Documentation
- API documentation: [docs/api.md](docs/api.md)
- Architecture overview: [docs/architecture.md](docs/architecture.md)

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- DeepSeek AI for providing the language model
- Filipino financial advisors for cultural context
- Flask community for the web framework
