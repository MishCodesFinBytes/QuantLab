from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Portfolio API", version="0.1.0")

# In-memory store (replaced by PostgreSQL in exercise 08)
_watchlist: dict[str, dict] = {}


class TickerIn(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)


class TickerOut(BaseModel):
    ticker: str


class PortfolioIn(BaseModel):
    tickers: list[str] = Field(..., min_length=1)
    weights: list[float] = Field(..., min_length=1)
    period: str = Field(default="1y")

    @model_validator(mode="after")
    def validate_lengths(self):
        if len(self.tickers) != len(self.weights):
            raise ValueError("tickers and weights must have the same length")
        return self


class AnalysisOut(BaseModel):
    tickers: list[str]
    weights: list[float]
    period: str
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/watchlist", response_model=list[TickerOut])
def list_watchlist():
    return list(_watchlist.values())


@app.post("/watchlist", response_model=TickerOut, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(body: TickerIn):
    ticker = body.ticker.upper()
    if ticker in _watchlist:
        raise HTTPException(status_code=409, detail=f"{ticker} already in watchlist")
    _watchlist[ticker] = {"ticker": ticker}
    return _watchlist[ticker]


@app.delete("/watchlist/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(ticker: str):
    ticker = ticker.upper()
    if ticker not in _watchlist:
        raise HTTPException(status_code=404, detail=f"{ticker} not in watchlist")
    del _watchlist[ticker]


@app.post("/analyze", response_model=AnalysisOut)
def analyze_portfolio(body: PortfolioIn):
    return AnalysisOut(
        tickers=body.tickers,
        weights=body.weights,
        period=body.period,
        message=f"Analysis stub for {len(body.tickers)} tickers over {body.period}",
    )
