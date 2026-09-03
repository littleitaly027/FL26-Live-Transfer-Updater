# FL26 Live Transfer Updater

**Automated Football Life 26 transfer database synchronizer with real-time squad updates**

## Overview

FL26 Live Transfer Updater automatically detects real-world football transfers from multiple sources and applies them to your Football Life 26 EDIT file. It features:

- **Automated Transfer Detection**: Monitors transfer sources for player movements
- **Smart Player Matching**: Matches external player data to your FL26 database
- **Data Protection**: Prevents accidental modification of player attributes
- **Confidence Scoring**: Uses AI to assess match quality before applying transfers
- **Backup & Rollback**: Automatic backups with easy restoration
- **GitHub Actions Integration**: Scheduled scans and cloud synchronization

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/littleitaly027/FL26-Live-Transfer-Updater.git
cd FL26-Live-Transfer-Updater

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`
2. Update with your settings:

```bash
# Path to your Football Life 26 EDIT00000000 file
EDIT_FILE=/path/to/EDIT00000000

# Scan intervals
SCAN_INTERVAL_MINUTES=15
DEEP_SCAN_INTERVAL_HOURS=6

# Confidence thresholds (0-100)
AUTO_APPLY_THRESHOLD=99      # Auto-apply only high-confidence matches
REVIEW_THRESHOLD=80          # Send medium-confidence to review queue
```

## Commands

### Scanning

```bash
# Fast scan for recently detected transfers
fl26-updater scan --dry-run

# Comprehensive deep scan
fl26-updater deep-scan --dry-run
```

## Architecture

### Core Modules

```
fl26_updater/
├── models.py              # Data models
├── database.py            # SQLite transfer history
├── cli.py                 # Command-line interface
├── sources/               # External data sources
├── matching/              # Player matching engine
├── protection/            # Data validation
└── edit/                  # EDIT file handling
```

## Development

### Testing

```bash
pytest tests/ -v --cov=fl26_updater
```

### Code Quality

```bash
black fl26_updater tests
ruff check fl26_updater tests
mypy fl26_updater
```

## License

MIT License

## Support

- 📝 [Create an Issue](https://github.com/littleitaly027/FL26-Live-Transfer-Updater/issues)
- 💬 [GitHub Discussions](https://github.com/littleitaly027/FL26-Live-Transfer-Updater/discussions)

---

**Happy transfers!** ⚽
