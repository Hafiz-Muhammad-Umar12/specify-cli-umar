# 📦 SpecKit Installation Guide

Follow these steps to get SpecKit up and running on your local machine.

## 📋 Prerequisites

- **Python**: 3.11 or higher.
- **Git**: Required for the autonomous commit feature.
- **API Keys**: Access to at least one supported LLM (OpenAI, Anthropic, or Google Gemini).

## 🛠️ Step 1: Install SpecKit

### Using Pip (Recommended)

```bash
pip install speckit-engine
```

### From Source (For Contributors)

```bash
git clone https://github.com/your-org/speckit.git
cd speckit
pip install -e .
```

## 🔑 Step 2: Configure Environment

SpecKit uses **LiteLLM** to manage provider connections. Set the environment variable for your preferred provider:

### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
```

### Anthropic (Claude)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Google Gemini
```bash
export GEMINI_API_KEY="AIza..."
```

*(Note: On Windows, use `set` instead of `export`, or use a `.env` file.)*

## 🧪 Step 3: Verify Installation

Run the version check to ensure everything is correct:

```bash
speckit --version
```

## 🚀 Next Steps

Try building your first autonomous project:

```bash
speckit run "A weather dashboard using the OpenWeather API"
```

Refer to the [Main README](../README.md) for advanced CLI commands and safety features.
