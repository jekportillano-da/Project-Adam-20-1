# Budget Buddy Mobile

An offline-first mobile budget calculator and savings tracker built with React Native and Expo.

## Features
- Input any budget amount and timeframe (daily/weekly/monthly)
- Get instant budget breakdowns tailored to Filipino context
- Receive practical financial advice based on local lifestyle
- Mobile-friendly interface

## Prerequisites
- Python 3.11 or higher
- DeepSeek API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jekportillano-da/Project-Adam-20-1.git
cd Project-Adam-20-1
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your DeepSeek API key
```

## Running the Application

1. Start the Flask server:
```bash
python run.py
```

2. Open your browser and navigate to:
```
http://localhost:8080
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
