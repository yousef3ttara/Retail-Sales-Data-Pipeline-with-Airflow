-- ============================================================
-- create_schema.sql
-- Run this ONCE in SSMS before running load_gold.py
-- Creates the gold schema and all 5 tables
-- ============================================================

-- Step 1: Create the gold schema
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'gold')
    EXEC('CREATE SCHEMA gold');
GO

-- ============================================================
-- DIMENSION TABLE 1: dim_car_models
-- Source: AU_Car_Models.csv (50 rows, clean)
-- ============================================================
IF OBJECT_ID('gold.dim_car_models', 'U') IS NOT NULL
    DROP TABLE gold.dim_car_models;
GO

CREATE TABLE gold.dim_car_models (
    Car_ID      INT             NOT NULL,
    Model       NVARCHAR(100)   NOT NULL,
    Make        NVARCHAR(100)   NOT NULL,
    Segment     NVARCHAR(50)    NOT NULL,   -- Sedan / SUV / Truck / Coupe
    MSRP        INT             NOT NULL,

    CONSTRAINT PK_dim_car_models PRIMARY KEY (Car_ID)
);
GO

-- ============================================================
-- DIMENSION TABLE 2: dim_dealers
-- Source: AU_Dealers.csv (48 rows, clean)
-- ============================================================
IF OBJECT_ID('gold.dim_dealers', 'U') IS NOT NULL
    DROP TABLE gold.dim_dealers;
GO

CREATE TABLE gold.dim_dealers (
    Dealer_ID           INT             NOT NULL,
    Country             NVARCHAR(100)   NULL,
    State               NVARCHAR(100)   NULL,
    City                NVARCHAR(100)   NULL,
    Zip_Code            INT             NULL,
    Address             NVARCHAR(255)   NULL,
    Dealer_Name         NVARCHAR(200)   NOT NULL,
    Contact_Name        NVARCHAR(200)   NULL,
    Contact_Phone_Number NVARCHAR(50)   NULL,
    Latitude            FLOAT           NULL,
    Longitude           FLOAT           NULL,

    CONSTRAINT PK_dim_dealers PRIMARY KEY (Dealer_ID)
);
GO

-- ============================================================
-- DIMENSION TABLE 3: dim_sentiment
-- Source: AU_Sentiment.csv (10,656 rows, clean)
-- ============================================================
IF OBJECT_ID('gold.dim_sentiment', 'U') IS NOT NULL
    DROP TABLE gold.dim_sentiment;
GO

CREATE TABLE gold.dim_sentiment (
    Postal_Code     INT             NOT NULL,
    Date            DATE            NULL,
    Sentiment       NVARCHAR(20)    NOT NULL,   -- Positive / Negative / Neutral
    Year            INT             NOT NULL
);
GO

CREATE INDEX IX_sentiment_postal ON gold.dim_sentiment (Postal_Code);
CREATE INDEX IX_sentiment_year   ON gold.dim_sentiment (Year);
GO

-- ============================================================
-- FACT TABLE 1: fact_daily_sales  (MAIN FACT)
-- Source: AU_Daily_Sales.csv (~52,683 rows after Silver cleaning)
-- ============================================================
IF OBJECT_ID('gold.fact_daily_sales', 'U') IS NOT NULL
    DROP TABLE gold.fact_daily_sales;
GO

CREATE TABLE gold.fact_daily_sales (
    Sales_ID                INT             NOT NULL,
    Count                   INT             NULL,
    Open_Date               DATE            NULL,
    Days_to_Make_Sale       INT             NULL,
    Car_ID                  INT             NULL,       -- FK -> dim_car_models
    Dealer_ID               INT             NULL,       -- FK -> dim_dealers
    Temperature_F           FLOAT           NULL,
    Temperature_Category    NVARCHAR(20)    NULL,       -- 0-10 / 11-20 / 21-30 / 31-40 / 41+
    Weather_Condition       NVARCHAR(50)    NULL,
    Humidity_Pct            FLOAT           NULL,
    Wind_Speed_mph          FLOAT           NULL,
    Wind_Gust_mph           FLOAT           NULL,
    Wind_Direction          NVARCHAR(10)    NULL,
    Visibility_mi           FLOAT           NULL,
    Wind_Chill_F            FLOAT           NULL,
    Precipitation_in        FLOAT           NULL,
    Fog_Y_N                 BIT             NULL,       -- Y/N converted to 1/0
    Rain_Y_N                BIT             NULL,
    Snow_Y_N                BIT             NULL,
    Month                   NVARCHAR(10)    NULL,       -- Jan / Feb / ...
    Month_Order             INT             NULL,       -- 1-12
    Year                    INT             NULL,

    CONSTRAINT PK_fact_daily_sales PRIMARY KEY (Sales_ID),
    CONSTRAINT FK_fact_daily_sales_car
        FOREIGN KEY (Car_ID) REFERENCES gold.dim_car_models (Car_ID),
    CONSTRAINT FK_fact_daily_sales_dealer
        FOREIGN KEY (Dealer_ID) REFERENCES gold.dim_dealers (Dealer_ID)
);
GO

CREATE INDEX IX_fact_ds_car_id    ON gold.fact_daily_sales (Car_ID);
CREATE INDEX IX_fact_ds_dealer_id ON gold.fact_daily_sales (Dealer_ID);
CREATE INDEX IX_fact_ds_year_month ON gold.fact_daily_sales (Year, Month_Order);
GO

-- ============================================================
-- FACT TABLE 2: fact_recalls  (SATELLITE FACT)
-- Source: AU_Car_Recalls.csv (~225 rows after Silver cleaning)
-- ============================================================
IF OBJECT_ID('gold.fact_recalls', 'U') IS NOT NULL
    DROP TABLE gold.fact_recalls;
GO

CREATE TABLE gold.fact_recalls (
    Recall_ID           INT IDENTITY(1,1)   NOT NULL,
    Date                DATE                NULL,
    Car_ID              INT                 NOT NULL,   -- FK -> dim_car_models
    System_Affected     NVARCHAR(100)       NULL,
    Units               INT                 NULL,
    Model               NVARCHAR(100)       NULL,

    CONSTRAINT PK_fact_recalls PRIMARY KEY (Recall_ID),
    CONSTRAINT FK_fact_recalls_car
        FOREIGN KEY (Car_ID) REFERENCES gold.dim_car_models (Car_ID)
);
GO

CREATE INDEX IX_recalls_car_id ON gold.fact_recalls (Car_ID);
GO

-- ============================================================
-- Verify all objects were created
-- ============================================================
SELECT
    s.name          AS schema_name,
    t.name          AS table_name,
    t.type_desc
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE s.name = 'gold'
ORDER BY t.name;
GO
