# Product Overview

## What is Stock Analysis Agent?

Stock Analysis Agent is a web-based AI-powered stock analysis service that provides comprehensive investment recommendations for publicly traded companies. The system uses a hierarchical multi-agent architecture powered by Google's Agent Development Kit (ADK) to perform deep financial analysis similar to how institutional investors analyze stocks.

## Problems It Solves

### 1. **Complex Financial Analysis Made Accessible**
Individual investors typically lack access to:
- Professional financial analyst teams
- Advanced quantitative analysis tools
- Comprehensive macro-economic analysis
- Real-time coordinated research capabilities

Stock Analysis Agent democratizes institutional-grade analysis by providing all these capabilities through a simple chat interface.

### 2. **Multi-Dimensional Analysis**
Traditional stock analysis tools provide fragmented information. Stock Analysis Agent solves this by:
- Coordinating multiple specialized analysts working in parallel
- Synthesizing diverse analytical perspectives (fundamental, technical, quantitative, macro)
- Providing a single comprehensive investment recommendation

### 3. **Real-Time Transparent Analysis**
Users can see the analysis process happening in real-time:
- Watch different agents thinking and working
- See which financial tools and APIs are being called
- Understand the reasoning behind investment recommendations
- Track progress through an activity timeline

## How It Works

### User Flow
1. **User Input**: User asks about a stock (e.g., "Analyze Tesla stock" or "AAPL 주식을 분석해줘")
2. **Multi-Agent Processing**: The system dispatches specialized agents in parallel and sequential patterns
3. **Real-Time Streaming**: User sees agents thinking, using tools, and analyzing data
4. **Final Report**: Hedge Fund Manager synthesizes all analyses into investment recommendation (BUY/SELL/HOLD)

### Agent Workflow

```
User Query
    ↓
Stock Analysis Department (Parallel)
    ├── Stock Researcher
    ├── Financial Team (Sequential)
    │   ├── Financial Analysts (Parallel)
    │   │   ├── Balance Sheet Analyst
    │   │   ├── Income Statement Analyst
    │   │   ├── Cash Flow Analyst
    │   │   └── Basic Financial Analyst
    │   └── Senior Financial Advisor (Synthesize)
    ├── Technical Analyst
    ├── Quantitative Team (Sequential)
    │   ├── Quant Analysts (Parallel)
    │   │   ├── Intrinsic Value Analyst
    │   │   └── Growth Analyst
    │   └── Senior Quantitative Advisor (Synthesize)
    └── Macro Economy Analyst
    ↓
Hedge Fund Manager (Final Synthesis)
    ↓
Investment Recommendation Report
```

### Key Capabilities

**Financial Analysis**
- Balance sheet analysis
- Income statement analysis
- Cash flow statement analysis
- Financial ratios and key metrics
- Year-over-year growth analysis

**Quantitative Analysis**
- DCF valuation
- Enterprise value calculation
- Owner earnings analysis
- Intrinsic value estimation

**Technical Analysis**
- Moving averages (long and mid-term)
- RSI (Relative Strength Index)
- ADX (Average Directional Index)
- Trend analysis

**Market Research**
- Stock news monitoring
- Analyst estimates
- Price target summaries
- Historical stock grades

**Macro Analysis**
- Economic indicators
- Market trends
- Global events impact

## Target Users

- **Individual Investors**: Seeking professional-grade analysis without institutional costs
- **Korean Investors**: Primary UI and reports in Korean language
- **Active Traders**: Need comprehensive analysis before making investment decisions
- **Financial Learners**: Want to understand how institutional analysis works

## Value Proposition

**Instead of:**
- Paying for multiple financial data subscriptions
- Spending hours researching across different sources
- Trying to interpret complex financial metrics
- Making decisions without comprehensive analysis

**Users get:**
- One-stop comprehensive analysis
- AI-powered institutional-grade insights
- Real-time transparent process
- Clear investment recommendations with rationale
- All in a simple chat interface

## Korean Market Focus

The system is specifically tailored for Korean users:
- Korean language UI and reports
- Supports both English ticker symbols (AAPL) and Korean company names (삼성전자)
- Korean-friendly date/time formatting
- Culturally appropriate report structure and terminology
- Emoji usage for better readability in Korean context