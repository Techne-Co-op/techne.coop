# Sources

Every number used in `shape.md` traces to one of these. Retrieval dates are the dates
this directory was assembled, 2026-08-17, unless stated otherwise.

## S1 · Federal occupational wage data

**BLS Occupational Employment and Wage Statistics (OEWS), May 2024 estimates.**
Metropolitan file `oesm24ma.zip` (`MSA_M2024_dl.xlsx`) and state file `oesm24st.zip`
(`state_M2024_dl.xlsx`).

- https://www.bls.gov/oes/special-requests/oesm24ma.zip
- https://www.bls.gov/oes/special-requests/oesm24st.zip
- Retrieved 2026-08-17.

Areas extracted: Boulder, CO MSA (area 14500); Denver-Aurora-Lakewood, CO MSA (area
19740); Colorado statewide. Rows for twenty-two occupation codes are in
`oews-may2024-boulder-denver-colorado.csv`, unmodified from the federal file except
for the column subset.

Notes a reader should carry:

- These are May 2024 estimates, so they are roughly two years stale as of this
  writing and predate the 2025 and 2026 local minimum wage steps in S2.
- `#` in a percentile column means the federal file suppressed the estimate (wages
  above the published cap). `**` in an employment column means employment was not
  released for that cell. Neither is a zero.
- The HTML rendering of these tables at bls.gov refuses automated retrieval. The
  bulk files above are the supported path and are what was used.

## S2 · Local statutory wage floors

**City of Boulder local minimum wage.** https://bouldercolorado.gov/local-minimum-wage
Retrieved 2026-08-17. Figures as published: 2025, $15.57 per hour; 2026, $16.82 per
hour; 2027, $18.17 per hour; from 2028, annual CPI-U adjustment for the
Denver-Aurora-Lakewood region. Established by Ordinance 8664.

**Colorado state minimum wage, 2026: $14.81 per hour.** Reported by several employer
compliance summaries retrieved 2026-08-17, for example
https://www.govdocs.com/colorados-new-minimum-wage-rates/ .
*Not verified against the Colorado Department of Labor and Employment order itself.*
The city figure is the binding one for work performed in Boulder and is the figure
used in `shape.md`; the state figure appears here only for context and carries this
caveat.

## S3 · Living wage

**MIT Living Wage Calculator, Boulder County, Colorado (FIPS 08013).**
https://livingwage.mit.edu/counties/08013 Retrieved 2026-08-17; the page reports its
data as updated 2026-02-15.

- 1 adult, 0 children: living wage $27.09/hr, poverty wage $7.67/hr
- 1 adult, 1 child: living wage $54.16/hr
- 2 adults both working, 2 children: living wage $38.60/hr
- Minimum wage as the calculator states it for the county: $15.16/hr (this differs
  from the City of Boulder figure in S2; the calculator is county-level and the
  ordinance is city-level)

## S4 · Cooperative sector comparison

**Democracy at Work Institute and the US Federation of Worker Cooperatives, 2019
Worker Cooperative State of the Sector report**, as reported by NCBA CLUSA:
https://ncbaclusa.coop/blog/worker-co-op-employees-now-earn-an-average-of-19-67-per-hour-according-to-new-report/
Retrieved 2026-08-17. Average worker co-op wage $19.67 per hour; the report finds
the large majority of worker cooperatives hold a 2:1 ratio between highest and
lowest paid worker. **2019 data.** Use the ratio, not the dollar figure: seven years
of inflation sit between that survey and this memo.

## S5 · A published cooperative rate schedule

**Hypha Worker Co-operative, employee salary guide.**
https://handbook.hypha.coop/How-we-work/salary.html Retrieved 2026-08-17. A tech
worker co-op in Canada that publishes its whole formula:

> Base Salary = 53,844 CAD * L^l * R^r * S^s * Modifiers + Adjustment

with Level L = 1.160 over l in 0 to 6, Responsibility R = 1.120 over r in 0 to 4,
Seniority S = 1.025 over s in 0 to 3, plus commitment, contractor, and geographic
modifiers. Its published base table runs 53,844 CAD at L0R0 to 206,423 CAD at L6R4,
stated for a four-day week.

Relevance is structural rather than numeric: the currency is Canadian, the market is
not Boulder, and the four-day week makes the annual figures non-comparable. What is
worth borrowing is that the schedule is a small number of named factors with published
multipliers, so any single person's rate is derivable and arguable rather than
negotiated in private.

## Sources looked for and not found

- No published rate schedule for a Colorado venture studio or a Boulder cooperative
  was found. If one exists it is not on the open web under the searches run here.
- Autonomic Co-operative and similar tech co-ops were checked for published day
  rates; their service pages do not publish them.
- Colorado state occupational data beyond the federal OEWS state file was not
  separately retrieved. CDLE republishes OEWS rather than producing an independent
  wage survey, so the state file in S1 is the same underlying estimate.
