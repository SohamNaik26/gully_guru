SELECT
    max({{col}}) AS {{col}}
FROM `{{project_id}}.raw.source_yfinance_{{statement_type}}`
WHERE ticker = "{{ticker}}";
