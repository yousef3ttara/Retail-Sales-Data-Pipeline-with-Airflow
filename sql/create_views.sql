-- ============================================================
-- create_views.sql
-- Run AFTER load_gold.py loads the tables
-- OR run manually in SSMS after tables have data
-- ============================================================

-- ============================================================
-- VIEW 1: v_monthly_by_model
-- Replaces AU_Sales_By_Model as an aggregated Gold view
-- Built from fact_daily_sales + dim_car_models + dim_dealers
-- ============================================================
CREATE OR ALTER VIEW gold.v_monthly_by_model AS
SELECT
    f.Year,
    f.Month_Order,
    f.Month,
    m.Model,
    m.Make,
    m.Segment,
    m.MSRP,
    d.City,
    d.State,
    COUNT(*)                    AS Total_Sales,
    AVG(f.Days_to_Sale)         AS Avg_Days_to_Close,
    MIN(f.Days_to_Sale)         AS Min_Days_to_Close,
    MAX(f.Days_to_Sale)         AS Max_Days_to_Close,
    AVG(f.Temperature_F)        AS Avg_Temp_F,
    SUM(CASE WHEN f.Is_Rain = 1 THEN 1 ELSE 0 END) AS Sales_on_Rain_Days,
    SUM(CASE WHEN f.Is_Snow = 1 THEN 1 ELSE 0 END) AS Sales_on_Snow_Days
FROM gold.fact_daily_sales      f
JOIN gold.dim_car_models        m ON f.Car_ID    = m.Car_ID
JOIN gold.dim_dealers           d ON f.Dealer_ID = d.Dealer_ID
GROUP BY
    f.Year, f.Month_Order, f.Month,
    m.Model, m.Make, m.Segment, m.MSRP,
    d.City, d.State;
GO

-- ============================================================
-- VIEW 2: v_dealer_performance
-- One row per dealer — total sales and avg close time
-- ============================================================
CREATE OR ALTER VIEW gold.v_dealer_performance AS
SELECT
    d.Dealer_ID,
    d.Dealer_Name,
    d.City,
    d.State,
    d.Zip_Code,
    d.Latitude,
    d.Longitude,
    COUNT(*)                    AS Total_Sales,
    AVG(f.Days_to_Sale)         AS Avg_Days_to_Close,
    MIN(f.Open_Date)            AS First_Sale_Date,
    MAX(f.Open_Date)            AS Last_Sale_Date,
    COUNT(DISTINCT f.Car_ID)    AS Distinct_Models_Sold
FROM gold.fact_daily_sales      f
JOIN gold.dim_dealers           d ON f.Dealer_ID = d.Dealer_ID
GROUP BY
    d.Dealer_ID, d.Dealer_Name, d.City, d.State,
    d.Zip_Code, d.Latitude, d.Longitude;
GO

-- ============================================================
-- VIEW 3: v_recall_risk
-- Joins fact_daily_sales + fact_recalls through dim_car_models
-- Shows recall rate per model relative to units sold
-- ============================================================
CREATE OR ALTER VIEW gold.v_recall_risk AS
SELECT
    m.Car_ID,
    m.Model,
    m.Make,
    m.Segment,
    m.MSRP,
    COUNT(DISTINCT f.Sales_ID)          AS Units_Sold,
    COALESCE(SUM(r.Units), 0)           AS Total_Units_Recalled,
    COUNT(DISTINCT r.Recall_ID)         AS Recall_Events,
    ROUND(
        100.0 * COALESCE(SUM(r.Units), 0)
              / NULLIF(COUNT(DISTINCT f.Sales_ID), 0),
        2
    )                                   AS Recall_Rate_Pct
FROM gold.fact_daily_sales              f
JOIN  gold.dim_car_models               m  ON f.Car_ID = m.Car_ID
LEFT JOIN gold.fact_recalls             r  ON m.Car_ID = r.Car_ID
GROUP BY
    m.Car_ID, m.Model, m.Make, m.Segment, m.MSRP;
GO

-- ============================================================
-- VIEW 4: v_weather_impact_on_sales
-- Does weather affect how fast cars sell?
-- ============================================================
CREATE OR ALTER VIEW gold.v_weather_impact AS
SELECT
    f.Weather_Condition,
    f.Temperature_Category,
    COUNT(*)                    AS Total_Sales,
    AVG(f.Days_to_Sale)         AS Avg_Days_to_Close,
    AVG(f.Temperature_F)        AS Avg_Temp_F,
    AVG(f.Humidity_Pct)         AS Avg_Humidity
FROM gold.fact_daily_sales      f
WHERE f.Weather_Condition IS NOT NULL
GROUP BY
    f.Weather_Condition,
    f.Temperature_Category;
GO

-- ============================================================
-- Verify all views were created
-- ============================================================
SELECT
    s.name      AS schema_name,
    v.name      AS view_name
FROM sys.views  v
JOIN sys.schemas s ON v.schema_id = s.schema_id
WHERE s.name = 'gold'
ORDER BY v.name;
GO

-- ============================================================
-- Quick sanity checks — run these after load_gold.py finishes
-- ============================================================

-- Check table row counts
SELECT 'fact_daily_sales'   AS table_name, COUNT(*) AS row_count FROM gold.fact_daily_sales  UNION ALL
SELECT 'fact_recalls',                      COUNT(*)              FROM gold.fact_recalls       UNION ALL
SELECT 'dim_car_models',                    COUNT(*)              FROM gold.dim_car_models     UNION ALL
SELECT 'dim_dealers',                       COUNT(*)              FROM gold.dim_dealers        UNION ALL
SELECT 'dim_sentiment',                     COUNT(*)              FROM gold.dim_sentiment;
GO

-- Check top 5 rows from each view
SELECT TOP 5 * FROM gold.v_monthly_by_model     ORDER BY Year, Month_Order;
SELECT TOP 5 * FROM gold.v_dealer_performance   ORDER BY Total_Sales DESC;
SELECT TOP 5 * FROM gold.v_recall_risk          ORDER BY Recall_Rate_Pct DESC;
SELECT TOP 5 * FROM gold.v_weather_impact       ORDER BY Total_Sales DESC;
GO
