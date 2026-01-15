# Quest 3 Comfort Analyzer

A web scraping and analysis tool for collecting Meta Quest 3 comfort-related reviews and accessory recommendations from multiple sources.

## Features

- **Multi-source scraping**: Reddit, Amazon, YouTube, Best Buy, VR forums
- **NLP Analysis**: Sentiment analysis and accessory extraction
- **Web Dashboard**: Interactive visualizations of accessory rankings and comfort issues

## Project Structure

```
quest3-comfort-analyzer/
├── scraper/           # Web scrapers for different sources
├── analyzer/          # NLP and sentiment analysis
├── backend/           # FastAPI backend
├── frontend/          # React dashboard
├── data/              # SQLite database
└── requirements.txt   # Python dependencies
```

## Setup

### 1. Install Python Dependencies

```bash
cd quest3-comfort-analyzer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Initialize Database

```bash
python backend/database.py
```

### 3. Configure API Keys (Optional)

Create a `.env` file for API keys:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=Quest3ComfortAnalyzer/1.0
YOUTUBE_API_KEY=your_youtube_api_key
```

### 4. Run Scrapers

```bash
# Run individual scrapers
python scraper/reddit_scraper.py
python scraper/amazon_scraper.py
python scraper/youtube_scraper.py

# Or run all at once
python run_scrapers.py
```

### 5. Analyze Data

```bash
python analyzer/sentiment.py
python analyzer/categorizer.py
```

### 6. Start Backend

```bash
uvicorn backend.main:app --reload
```

### 7. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## Data Sources

| Source | Method | Notes |
|--------|--------|-------|
| Reddit | PRAW API / JSON endpoint | r/OculusQuest, r/Quest3, r/metaquest |
| Amazon | Web scraping | Quest 3 accessory reviews |
| YouTube | YouTube Data API | Comments on comfort videos |
| Best Buy | Web scraping | Product reviews |
| VR Forums | Web scraping | UploadVR, Road to VR |

## Tracked Accessories

- **Head Straps**: BoboVR M3 Pro, Kiwi Elite, Meta Elite Strap, AMVR, DESTEK
- **Face Covers**: VR Cover, AMVR, Kiwi, silicone covers
- **Battery Packs**: BoboVR, Anker, Meta Elite Battery
- **Lens Protectors**: ZenGuard, prescription inserts
- **Other**: Controller grips, cases, comfort mods

## API Endpoints

- `GET /api/rankings` - Accessory rankings by sentiment
- `GET /api/issues` - Comfort issues breakdown
- `GET /api/sources` - Data source distribution
- `GET /api/accessory/{name}` - Detailed accessory info

## License

MIT
# quest3-comfort-analyzer
