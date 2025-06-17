# Advanced SQL Queries for Database Course Requirements

This directory contains 5 sophisticated SQL queries that demonstrate mastery of advanced database concepts required for university-level database courses.

## Query Complexity Overview

### 🎯 Query 1: User Performance Analytics with Rankings
**Complexity Level:** High  
**Demonstrates:**
- Complex JOINs across 4+ tables (users, bets, rounds, games)
- Window functions (RANK() OVER)
- Common Table Expressions (CTEs) for modular query design
- Aggregate functions with GROUP BY and HAVING
- Conditional aggregations using CASE statements
- Advanced calculations (ROI, win percentages)

**Business Value:** Provides comprehensive user profitability analysis and risk assessment

### 🎰 Query 2: Game Revenue and Performance Analysis  
**Complexity Level:** High  
**Demonstrates:**
- Multi-level CTEs for staged calculations
- Business logic implementation in SQL
- Date/time calculations with EXTRACT
- Complex percentage calculations
- Ranking functions for comparative analysis
- Performance metrics across multiple dimensions

**Business Value:** Evaluates game profitability and house edge efficiency

### 🐎 Query 3: Horse Racing Performance Analytics
**Complexity Level:** Very High  
**Demonstrates:**
- Complex multi-table JOINs across 5+ tables
- Statistical calculations (averages, minimums)
- JSON field querying with PostgreSQL operators
- Composite foreign key relationships
- Performance tier classification algorithms
- Betting pattern correlation analysis

**Business Value:** Advanced horse performance metrics and betting analytics

### 💰 Query 4: Transaction Pattern Analysis
**Complexity Level:** High  
**Demonstrates:**
- Financial behavior analysis
- Date-based calculations and time series analysis
- Multiple conditional aggregations
- Financial health scoring algorithms
- Null-safe calculations with COALESCE and NULLIF
- User segmentation based on spending patterns

**Business Value:** Customer financial health assessment and risk profiling

### 📊 Query 5: Betting Behavior and Cohort Analysis
**Complexity Level:** Very High  
**Demonstrates:**
- Cohort analysis methodology
- User lifecycle tracking
- Retention metrics calculation
- Behavioral segmentation algorithms
- Statistical variance calculations (STDDEV)
- Customer lifetime value analysis
- Temporal data analysis with DATE_TRUNC

**Business Value:** User retention analysis and behavioral insights

## Database Concepts Demonstrated

### Core SQL Features
- ✅ Complex JOINs (INNER, LEFT, multiple tables)
- ✅ Subqueries and correlated subqueries
- ✅ Window functions (RANK, ROW_NUMBER, partitioning)
- ✅ Common Table Expressions (CTEs)
- ✅ Aggregate functions (SUM, COUNT, AVG, MIN, MAX, STDDEV)
- ✅ GROUP BY with HAVING clauses
- ✅ CASE statements for conditional logic

### Advanced Features
- ✅ Date/time functions and calculations
- ✅ JSON field querying (PostgreSQL specific)
- ✅ Null handling (COALESCE, NULLIF)
- ✅ Mathematical operations and rounding
- ✅ String manipulation and formatting
- ✅ Type casting and data conversion

### Business Intelligence Concepts
- ✅ Cohort analysis
- ✅ Customer segmentation
- ✅ Performance ranking
- ✅ Financial health scoring
- ✅ Retention metrics
- ✅ Statistical analysis

## Running the Queries

### Command Line Execution
```bash
# Execute all 5 complex queries
python analytics/complex_queries.py

# Or run individual queries programmatically
python -c "
from analytics.complex_queries import query_1_user_performance_analytics
query_1_user_performance_analytics()
"
```

### Web Interface
1. Log in as an admin user
2. Navigate to Admin Dashboard
3. Click "Advanced Analytics" button
4. View results in formatted tables

### Direct Database Access
```sql
-- Connect to PostgreSQL database
psql -h localhost -U casino -d casino_db

-- Execute individual queries (copy from complex_queries.py)
```

## Academic Compliance

These queries meet or exceed typical database course requirements for:

- **Intermediate Database Courses:** Queries 1-2 demonstrate solid understanding
- **Advanced Database Courses:** Queries 3-5 show mastery of complex concepts
- **Database Analytics Courses:** All queries provide real-world business intelligence
- **Data Science Courses:** Queries 4-5 include statistical and behavioral analysis

## Real-World Application

Each query solves actual business problems:

1. **Customer Profitability Analysis** - Identify high-value customers
2. **Game Performance Optimization** - Optimize game offerings
3. **Sports Betting Analytics** - Advanced horse racing insights  
4. **Financial Risk Assessment** - Detect problem gambling patterns
5. **User Experience Optimization** - Improve user retention

## Technical Specifications

- **Database:** PostgreSQL 16+
- **Framework:** SQLAlchemy with Flask
- **Features Used:** JSON fields, Window functions, CTEs
- **Performance:** Optimized with proper indexing on foreign keys
- **Scalability:** Designed for datasets with 100K+ records

## Sample Output

Each query produces structured results showing:
- Quantitative metrics and KPIs
- Categorical classifications and tiers
- Rankings and comparative analysis
- Actionable business insights

This demonstrates both technical SQL proficiency and business acumen required for database professionals. 