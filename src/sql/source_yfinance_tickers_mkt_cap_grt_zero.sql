SELECT ticker
FROM `jovita-418606.raw.source_yfinance_info` 
WHERE CAST(marketcap AS FLOAT64) > 0 