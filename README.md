# 📊 SEC 10-K RAG Agent

A Retrieval-Augmented Generation (RAG) application that analyzes SEC 10-K filings to answer financial questions about major tech companies using AI.

## 🎯 Overview

This application uses advanced AI techniques to process and analyze SEC 10-K financial filings from major technology companies (Google/Alphabet, Microsoft, NVIDIA) spanning 2022-2024. Users can ask natural language questions about financial performance, business segments, risks, and other business insights.

### Key Features

- 🤖 **AI-Powered Analysis** - Uses OpenAI GPT models with RAG for accurate financial insights
- 📄 **Real SEC Data** - Processes actual 10-K filings from SEC EDGAR database
- 🔍 **Smart Search** - Company and year-aware document retrieval
- 💬 **Chat Interface** - User-friendly Streamlit web application
- 📊 **Source Citations** - Every answer includes exact page references
- ⚡ **Fast Queries** - Pre-processed vector embeddings for quick responses

### Supported Companies & Years

| Company | Ticker | Years |
|---------|--------|-------|
| Alphabet Inc. (Google) | GOOGL | 2022, 2023, 2024 |
| Microsoft Corporation | MSFT | 2022, 2023, 2024 |
| NVIDIA Corporation | NVDA | 2022, 2023, 2024 |

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SEC 10-K      │    │   Vector Store   │    │   Streamlit     │
│   PDF Files     │───▶│   (ChromaDB)     │───▶│   Web App       │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   OpenAI         │    │   LangChain     │
                       │   Embeddings     │    │   Agent         │
                       └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- OpenAI API key
- Internet connection for downloading SEC filings

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd uniqus-assignment

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Download SEC Filings

Create a `data/` directory and download SEC 10-K filings with these exact filenames:

```
data/
├── GOOGL_2022.pdf
├── GOOGL_2023.pdf
├── GOOGL_2024.pdf
├── MSFT_2022.pdf
├── MSFT_2023.pdf
├── MSFT_2024.pdf
├── NVDA_2022.pdf
├── NVDA_2023.pdf
└── NVDA_2024.pdf
```

#### Option A: Automated Download (Recommended)
```bash
cd src
python main.py --download
```

#### Option B: Manual Download
Visit the [SEC EDGAR Company Search](https://www.sec.gov/edgar/searchedgar/companysearch.html):

1. **Search for each company** (Microsoft, Google, NVIDIA)
2. **Filter by "10-K" filings**
3. **Download the most recent filings** for 2022, 2023, 2024
4. **Save with exact filenames** as shown above

**Alternative Sources:**
- [Microsoft Investor Relations](https://www.microsoft.com/en-us/Investor/)
- [Alphabet Investor Relations](https://abc.xyz/investor/)
- [NVIDIA Investor Relations](https://investor.nvidia.com/)

### 4. Launch Application

```bash
cd src
streamlit run app.py
```

The application will:
1. **Automatically process** all PDF files (first run takes 3-5 minutes)
2. **Build vector embeddings** using OpenAI
3. **Launch web interface** at http://localhost:8501

## 💻 Usage

### Web Interface

1. **Open** http://localhost:8501 in your browser
2. **Type questions** in the chat input at the bottom
3. **View structured answers** with source citations
4. **Explore chat history** and previous queries

### Sample Questions

#### Financial Performance
```
"What was Microsoft's total revenue in fiscal year 2024?"
"Compare NVIDIA's revenue growth between 2022 and 2023"
"Which company had the highest operating margin in 2023?"
```

#### Business Analysis
```
"What are Google's main business segments?"
"How did Microsoft's cloud business perform in 2023?"
"What are the main risk factors mentioned by NVIDIA?"
```

#### Comparative Analysis
```
"Compare the R&D spending of all three companies in 2023"
"Which company has the strongest growth trajectory?"
"What are the key differences in business models?"
```

### Response Format

Each answer includes:

- **Answer:** Direct response to your question
- **Reasoning:** How the AI approached the analysis
- **Sources:** Exact page references with excerpts
- **Sub-queries:** Search terms used internally

Example:
```json
{
  "query": "What was Microsoft's revenue in 2024?",
  "answer": "Microsoft's total revenue for fiscal year 2024 was $245.1 billion...",
  "reasoning": "I searched Microsoft's 2024 10-K filing and found revenue data...",
  "sources": [
    {
      "ticker": "MSFT",
      "year": "2024", 
      "page": 36,
      "file": "MSFT_2024.pdf",
      "excerpt": "Total revenue increased 16% to $245.1 billion..."
    }
  ]
}
```

## 🛠️ Technical Details

### Dependencies

**Core AI Stack:**
- `langchain` - LLM orchestration and RAG pipeline
- `langchain-openai` - OpenAI model integration
- `langchain-chroma` - Vector database integration
- `openai` - OpenAI API client

**Document Processing:**
- `pdfplumber` - PDF text extraction
- `beautifulsoup4` - HTML parsing
- `tiktoken` - Token counting and chunking

**Vector Storage:**
- `chromadb` - Vector database for embeddings
- `python-dotenv` - Environment variable management

**Web Interface:**
- `streamlit` - Web application framework

### Document Processing Pipeline

1. **Text Extraction** - Extract text from PDF/HTML files
2. **Chunking** - Split documents into 500-token chunks with 100-token overlap
3. **Embedding** - Generate OpenAI embeddings for each chunk
4. **Storage** - Store in ChromaDB vector database with metadata
5. **Retrieval** - Smart search with company/year filtering

### Performance Specifications

- **Processing Time:** 3-5 minutes for initial setup (9 documents, ~2,200 chunks)
- **Storage Size:** ~35MB vector database
- **Query Response:** 2-10 seconds per question
- **Embedding Model:** OpenAI text-embedding-3-small
- **Chat Model:** GPT-4o-mini

## 🔧 Advanced Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_api_key

# Optional
PERSIST_DIR=chroma_store        # Vector database location
DATA_DIR=data                   # SEC filing location
EMBED_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
```

### Customizing Document Sources

To add new companies or years:

1. **Add PDF files** to `data/` with format `TICKER_YEAR.pdf`
2. **Update config.py** with new company tickers
3. **Rebuild vector store** by deleting `chroma_store/` folder

### Command Line Interface

```bash
cd src

# Process documents and answer question
python main.py --q "Your question here"

# Download new filings
python main.py --download

# Custom question
python main.py --q "Compare revenue growth rates"
```

## 🧪 Testing & Verification

### Test File Verification

```bash
python verify_files.py
```

Checks:
- ✅ All 9 required files present
- ✅ File sizes reasonable (1-10MB each)
- ✅ Content contains financial terms

### Sample Test Queries

Run these to verify functionality:

```python
# Basic functionality
"What companies are in this database?"

# Specific data retrieval  
"Microsoft revenue 2024"

# Multi-company analysis
"Compare operating margins across all companies"

# Complex analysis
"What are the biggest risks facing these tech companies?"
```

## 📁 Project Structure

```
uniqus-assignment/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables
├── data/                    # SEC 10-K filings
│   ├── GOOGL_2022.pdf
│   ├── MSFT_2023.pdf
│   └── ...
├── chroma_store/           # Vector database (auto-generated)
└── src/                    # Source code
    ├── app.py             # Streamlit web application
    ├── main.py            # Command line interface
    ├── config.py          # Configuration settings
    ├── agent_runner.py    # LLM agent orchestration
    ├── agent_tools.py     # RAG tools and search logic
    ├── build_index.py     # Vector store construction
    ├── preprocess.py      # Document processing
    └── download_filings.py # SEC filing downloader
```

## 🐛 Troubleshooting

### Common Issues

**"No relevant documents found"**
- Verify PDF files are in `data/` directory
- Check file naming convention matches exactly
- Try rephrasing your question

**"Agent stopped due to max iterations"**
- Question might be too complex
- Try more specific queries
- Break complex questions into parts

**"Vector store building fails"**
- Check OpenAI API key is valid
- Ensure sufficient API credits
- Verify internet connection

**"Module not found errors"**
- Activate virtual environment: `source .venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Performance Issues

**Slow initial startup:**
- Normal for first run (building vector store)
- Subsequent runs should be fast

**Large memory usage:**
- Vector store requires ~2GB RAM
- Consider smaller chunk sizes if needed

### API Limits

**Rate limiting:**
- Built-in delays between API calls
- Automatic retry logic for failures
- Uses small batch sizes (20 chunks)

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repo-url>
cd uniqus-assignment

# Setup development environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install development tools
pip install black flake8 pytest
```

### Code Style

- Use `black` for code formatting
- Follow PEP 8 guidelines
- Add docstrings for new functions
- Include type hints where appropriate

### Adding New Features

1. **Document processing improvements** - Modify `preprocess.py`
2. **Search enhancements** - Update `agent_tools.py`
3. **UI changes** - Edit `app.py`
4. **New data sources** - Extend `download_filings.py`

## 📝 License

This project is for educational and research purposes. SEC filings are public domain. Please respect OpenAI's usage policies and rate limits.

## 🙏 Acknowledgments

- **SEC EDGAR** - Public financial data source
- **OpenAI** - Language models and embeddings
- **LangChain** - RAG framework
- **Streamlit** - Web application framework
- **ChromaDB** - Vector database solution

---

**Built as an Assignment for Uniqus**

For questions or issues, please check the troubleshooting section or open an issue on GitHub.
