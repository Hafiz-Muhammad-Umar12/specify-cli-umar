# Contributing to SpecKit

First off, thank you for considering contributing to SpecKit! It's people like you that make SpecKit such a great tool.

## 🏗️ Development Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/your-org/speckit.git
   cd speckit
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Set up your environment:**
   Copy `.env.example` to `.env` and add your API keys.

## 🧪 Testing

We use `pytest` for all internal logic.
```bash
pytest
```

## 📝 Guidelines

### Code Style
- We follow PEP 8.
- Use type hints for all public functions.
- Every new agent or engine feature MUST have corresponding unit tests.

### PR Process
1. Fork the repo and create your branch from `main`.
2. Ensure the DAG engine still passes a full dry-run.
3. Open a PR with a clear description of the "Why" and "What".
4. Wait for the SpecKit Reviewer agent (and a human) to sign off!

## ⚖️ License
By contributing, you agree that your contributions will be licensed under its MIT License.
