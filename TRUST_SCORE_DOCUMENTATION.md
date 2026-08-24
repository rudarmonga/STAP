# STAP Trust Score Documentation

## Overview

The STAP Trust Score is a deterministic, explainable metric (0-100 scale) that assesses seller performance and reliability based on measurable marketplace data. The score is designed to help marketplace managers and operations teams identify sellers who require monitoring or intervention.

## Score Range

- **0-100**: Trust Score range
- **Higher scores**: Better seller performance and reliability
- **Lower scores**: Poor performance and higher risk

## Risk Classification

Based on Trust Score, sellers are classified into three risk levels:

- **Healthy (80-100)**: Sellers with strong performance metrics
- **Monitor (60-79)**: Sellers requiring attention and monitoring
- **High Risk (0-59)**: Sellers with significant performance issues

## Trust Score Components

The Trust Score is calculated from five weighted components:

### 1. Rating Component (30% weight)

**Purpose**: Measures customer satisfaction through product ratings

**Data Source**: Average of customer ratings (1-5 scale)

**Normalization**: 
- Rating 1.0 → 0 points
- Rating 3.0 → 50 points  
- Rating 5.0 → 100 points

**Missing Data Handling**: If seller has no ratings, uses neutral score (50 points)

**Rationale**: Customer ratings are a direct measure of product quality and customer satisfaction, making them the most important component.

### 2. Return Component (25% weight)

**Purpose**: Measures product quality and customer satisfaction through return behavior

**Data Source**: Return rate (returns / total orders × 100)

**Normalization**:
- 0% return rate → 100 points
- 10% return rate → 50 points
- 20%+ return rate → 0 points

**Missing Data Handling**: If seller has no orders, uses neutral score (50 points)

**Rationale**: High return rates indicate product quality issues or misleading descriptions, which negatively impact customer trust.

### 3. Sentiment Component (20% weight)

**Purpose**: Measures customer sentiment through review text analysis

**Data Source**: Average sentiment score from reviews (-1 to +1 scale)

**Normalization**:
- Sentiment -1.0 → 0 points
- Sentiment 0.0 → 50 points
- Sentiment +1.0 → 100 points

**Missing Data Handling**: If seller has no reviews, uses neutral score (50 points)

**Rationale**: Review sentiment provides nuanced feedback beyond ratings, capturing customer experiences and satisfaction levels.

### 4. Operational Component (15% weight)

**Purpose**: Measures operational efficiency through delivery performance

**Data Source**: Average delivery days for completed orders

**Normalization**:
- 1 day delivery → ~90 points
- 5 days delivery → ~45 points
- 10+ days delivery → 0 points

**Missing Data Handling**: If seller has no delivery data, uses neutral score (50 points)

**Rationale**: Fast, reliable delivery is crucial for customer satisfaction and marketplace reputation.

### 5. Reliability Component (10% weight)

**Purpose**: Measures order fulfillment reliability

**Data Source**: Order completion rate (completed orders / total orders × 100)

**Normalization**:
- 100% completion → 100 points
- 50% completion → 50 points
- 0% completion → 0 points

**Missing Data Handling**: If seller has no orders, uses neutral score (50 points)

**Rationale**: High cancellation rates indicate reliability issues that damage customer trust.

## Trust Score Formula

```
Trust Score = 
  (Rating Component × 0.30) +
  (Return Component × 0.25) +
  (Sentiment Component × 0.20) +
  (Operational Component × 0.15) +
  (Reliability Component × 0.10)
```

All components are normalized to a 0-100 scale before weighting.

## Example Calculation

Consider a seller with the following metrics:
- Average rating: 4.2/5.0
- Return rate: 8%
- Average sentiment: 0.3
- Average delivery days: 4 days
- Completion rate: 95%

**Component calculations:**
1. Rating: (4.2 - 1.0) / (5.0 - 1.0) × 100 = 80 points
2. Return: 100 - (8.0 / 20.0 × 100) = 60 points
3. Sentiment: (0.3 - (-1.0)) / (1.0 - (-1.0)) × 100 = 65 points
4. Operational: 100 - (4.0 / 10.0 × 90) = 64 points (with minimum score adjustment)
5. Reliability: 95 points

**Weighted score:**
- Rating: 80 × 0.30 = 24.0
- Return: 60 × 0.25 = 15.0
- Sentiment: 65 × 0.20 = 13.0
- Operational: 64 × 0.15 = 9.6
- Reliability: 95 × 0.10 = 9.5

**Final Trust Score:** 24.0 + 15.0 + 13.0 + 9.6 + 9.5 = **71.1** (Monitor)

## Data Sufficiency Requirements

To ensure reliable Trust Score calculations, minimum data requirements are enforced:

- **Minimum orders**: 5 orders
- **Minimum ratings**: 3 ratings (for rating component reliability)
- **Minimum reviews**: 2 reviews (for sentiment component reliability)

**Primary requirement**: Seller must have at least 5 orders to be considered for reliable assessment.

Sellers with insufficient data are flagged in the analytics results, and missing components use neutral scores (50 points) rather than assuming perfect performance.

## Limitations and Considerations

### Current Limitations

1. **Historical Weighting**: All time periods are weighted equally; recent performance may be more relevant
2. **Category Differences**: No adjustment for different return rate expectations across product categories
3. **Volume Independence**: Large and small sellers are evaluated on the same relative metrics
4. **Seasonal Effects**: No adjustment for seasonal variations in performance
5. **New Seller Penalty**: New sellers with limited data may receive neutral scores regardless of actual performance

### Future Enhancements

Potential improvements for future iterations:

1. **Time-weighted scoring**: Give more weight to recent performance
2. **Category-specific thresholds**: Adjust return rate expectations by product category
3. **Volume adjustments**: Consider order volume in risk assessment
4. **Trend analysis**: Incorporate performance trajectory (improving vs declining)
5. **Customer segment analysis**: Different scoring for different customer types

## Configuration

All Trust Score parameters are configurable in `src/analytics/config.py`:

- **Weights**: `TrustScoreWeights` class
- **Risk thresholds**: `RiskThresholds` class  
- **Data sufficiency**: `DataSufficiencyThresholds` class

To modify the Trust Score calculation:

1. Update weight values in `TrustScoreWeights` (must sum to 1.0)
2. Adjust risk thresholds in `RiskThresholds`
3. Modify data sufficiency requirements in `DataSufficiencyThresholds`
4. Update normalization functions in `src/analytics/normalization.py` if needed

## Reproducibility

The Trust Score calculation is deterministic:
- Same input data → Same Trust Score
- No randomness in the calculation
- All normalization and weighting rules are explicitly defined

This ensures consistent seller assessment over time and enables comparison of seller performance across different periods.

## Accessibility

The Trust Score is designed to be explainable:
- Each component score is visible in analytics results
- Weighting scheme is transparent
- Normalization methods are documented
- Risk classification thresholds are clear

Users can understand why a seller received a particular score and which areas need improvement.