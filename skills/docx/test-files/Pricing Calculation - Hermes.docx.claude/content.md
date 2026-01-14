# Pricing Calculation - Hermes Program

## 1. Base Rate

Read Base Rate from the table below. 6.125% rate has base price 99.75%, and 6.25% Rate has price at par.

| Rate Guide as of | Program | Rate | Base Price | Margin | Index |
|------------------|---------|------|------------|--------|-------|
| 9/15/2025 | 7/6 Mo. ARM (5/1/5) | 6.125% | 99.75* | 3.000% | 30-Day Avg. |
| | | 6.250% | 100.00* | | |

*Pricing is subject to change without notice. Investor exception approvals may include a 0.125 to 0.5 point charge.

---

## 2. Rate Adjustment

### Rate Adjustments by Loan Amount and FICO

| Rate Adjustments | FICO/CLTV | <=60 | 60.01-65 | 65.01-70 | 70.01-75 |
|------------------|-----------|------|----------|----------|----------|
| Loan Amount ≤ $2MM | 700+ | 0.000% | 0.000% | 0.250% | 0.375% |
| | 680-699 | 0.125% | 0.125% | 0.375% | 0.375% |
| $2MM < Loan Amount ≤ $3MM | 680+ | 0.125% | 0.125% | 0.375% | 0.500% |
| $3MM < Loan Amount ≤ $4MM | 720+ | 0.125% | 0.250% | 0.375% | |

### Rate Adjustments (Other Terms)

| Adjustment Type | <=60 | 60.01-65 | 65.01-70 | 70.01-75 |
|-----------------|------|----------|----------|----------|
| Cash-Out | 0.000% | 0.250% | 0.375% | 0.500% |
| Condominium | 0.000% | 0.125% | 0.375% | |
| 2-4 Unit | 0.125% | 0.125% | 0.125% | 0.250% |
| Units + ADU (See ADU guidelines below) | 0.125% | 0.125% | 0.250% | 0.375% |
| Investment Property | 0.125% | 0.250% | 0.250% | 0.375% |
| Self-Prepared P&L Statement | 0.500% | 0.500% | 0.500% | 0.500% |
| Asset Based Income Option (ABIO) | 0.500% | 0.500% | 0.500% | 0.500% |
| Banks Statement Options (3MB & BBS) | 0.125% | 0.125% | 0.125% | 0.125% |
| Foreign National | 0.500% | | | |
| 30 Year Fixed | 0.250% | 0.250% | 0.250% | 0.250% |

---

## 3. Loan Amount/FICO

Check loan amount, FICO and CLTV (if CLTV is not provided, assume CLTV = LTV or AI asks for more information)

**Example:**
If Loan amount <=2mm and FICO >=700, LTV <=60, rate adjustment = 0, if LTV is 60.01 to 65%, rate adjustment =0, if LTV is 65.01 to 70%, rate adjustment = 0.25%, if LTV is 70.01 to 75%, rate adjustment = 0.375%

---

## 4. Cash-Out

If loan purpose = cash out, check LTV and use this table.

| Rate Adjustments (Other Terms) | <=60 | 60.01-65 | 65.01-70 | 70.01-75 |
|--------------------------------|------|----------|----------|----------|
| Cash-Out | 0.000% | 0.250% | 0.375% | 0.500% |

Rate Adjustment = Rate Adjustment from Step 3 +
- 0% (if LTV <=60%)
- 0.25% (60.01 <= LTV <= 65%)
- 0.375% (65.01 <= LTV <= 70%)
- 0.5% (70.01 <= LTV <= 75%)

---

## 5-11. Other Adjustments

5. **Condo**: check property type and LTV
6. **Units + ADU**: check units and LTV
7. **Investment property**: check Occupancy and LTV
8. **Self-Prepared P&L statement**: Check Documentation Type and LTV
9. **Asset Based Income**: check documentation type and LTV
10. **Bank Statement**: check documentation type and LTV
11. **Foreign National**: if the borrower is foreign, check LTV
12. **Loan program**: if it's 30yr fixed, check LTV

---

## 13. Example Calculation

**Scenario:**
- Loan Amount: $2MM
- FICO: 720
- LTV: 68%
- Cash Out
- 2-4 Units
- Investment property
- Bank Statement
- 30 year fixed

**Rate Adjustment Calculation:**

| Adjustment Type | Amount |
|-----------------|--------|
| Loan Amount/FICO/LTV | 0.25% |
| Cash Out | 0.375% |
| 2-4 Units | 0.125% |
| Investment Property | 0.25% |
| Bank Statement | 0.125% |
| 30 yr fixed | 0.25% |
| **Total Rate Adjustment** | **1.375%** |

**Final Rate = Base Rate + Rate Adjustment**

| Program | Rate | Price |
|---------|------|-------|
| Hermes 7/6 ARM | 7.5% (6.125 + 1.375) | 99.75 |
| | 7.625% (6.25 + 1.375) | 100 |

---

## 14. Extension

AI asks if extension is needed, if so:

| Extension Days | Extension Fee Costs |
|----------------|---------------------|
| 7-Day | 0.125% from price |
| 15-Day | 0.250% from price |

---

## Mortgage Terms Reference

### Documentation Types
1. Full Doc
2. Bank Statement
3. P&L
4. Asset Based / Asset Utilization
5. 1099
6. WVOE

### Occupancy Types
1. Primary
2. Investment Property
3. Second Home
4. Vacant

### Loan Purpose
1. Cash Out
2. Purchase
3. Rate/Term Refi

### Property Types
1. SFR (Single Family Residential)
2. Condo
3. 2-4 units
4. Multi-family 5+ Units
