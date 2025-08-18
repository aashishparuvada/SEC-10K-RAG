from typing import List
from langchain_core.tools import Tool
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma

# Simple safe eval for arithmetic (growth %, sums)
def _safe_math(expr: str) -> str:
    import math
    allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    allowed["__builtins__"] = {}
    try:
        val = eval(expr, allowed, {})
        return str(val)
    except Exception as e:
        return f"Error: {e}"

def make_tools(vectorstore: Chroma) -> List[Tool]:
    # Create a smarter retriever that can filter by company and year
    def smart_search(query: str) -> str:
        """Enhanced search that can filter by company and year mentioned in query."""
        # Parse query for company names and years
        companies = []
        years = []
        
        query_upper = query.upper()
        if "MICROSOFT" in query_upper or "MSFT" in query_upper:
            companies.append("MSFT")
        if "GOOGLE" in query_upper or "ALPHABET" in query_upper or "GOOGL" in query_upper:
            companies.append("GOOGL")
        if "NVIDIA" in query_upper or "NVDA" in query_upper:
            companies.append("NVDA")
            
        # Extract years
        for year in ["2022", "2023", "2024"]:
            if year in query:
                years.append(year)
        
        # Build search filter
        search_kwargs = {"k": 12}  # Get more results initially
        
        # First try with semantic search
        retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
        docs = retriever.invoke(query)
        
        # Filter results if we detected specific companies or years
        if companies or years:
            filtered_docs = []
            for doc in docs:
                metadata = doc.metadata
                
                # Check company filter
                if companies and metadata.get("ticker") not in companies:
                    continue
                    
                # Check year filter  
                if years and metadata.get("year") not in years:
                    continue
                    
                filtered_docs.append(doc)
            
            # Use filtered results if we have enough, otherwise fall back to all results
            if len(filtered_docs) >= 3:
                docs = filtered_docs[:8]  # Limit to top 8 results
        
        # Format results for agent
        result_parts = []
        for i, doc in enumerate(docs[:8]):
            metadata = doc.metadata
            result_parts.append(
                f"Document {i+1}:\n"
                f"Company: {metadata.get('ticker', 'Unknown')}\n"
                f"Year: {metadata.get('year', 'Unknown')}\n"
                f"Page: {metadata.get('page', 'Unknown')}\n"
                f"File: {metadata.get('file', 'Unknown')}\n"
                f"Content: {doc.page_content}\n"
                f"---"
            )
        
        return "\n".join(result_parts) if result_parts else "No relevant documents found."
    
    retriever_tool = Tool(
        name="sec_10k_search",
        description=(
            "Search over chunked 10-K filings for GOOGL, MSFT, NVDA (years 2022-2024). "
            "Use this to find operating margin, revenue, segment results, risks, and MD&A insights. "
            "The tool automatically filters by company and year if mentioned in the query. "
            "Examples: 'Microsoft revenue 2023', 'NVIDIA operating margin', 'Google business segments 2024'"
        ),
        func=smart_search
    )

    math_tool = Tool(
        name="calculator",
        description="Evaluate simple arithmetic expressions, e.g., '(27.0-20.1)/20.1*100' to compute growth percent.",
        func=_safe_math,
    )

    return [retriever_tool, math_tool]
