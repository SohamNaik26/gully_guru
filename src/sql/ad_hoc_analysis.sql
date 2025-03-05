SELECT 
    bs.ticker, SUM(bs.value) AS total_value, i.industry
FROM jovita-418606.raw.source_yfinance_balance_sheet AS bs
JOIN jovita-418606.raw.source_yfinance_info AS i ON bs.ticker = i.ticker
WHERE i.industry ='Travel Services' and bs.kpi ='Total Assets'
GROUP BY i.industry,bs.ticker
order by total_value desc;
