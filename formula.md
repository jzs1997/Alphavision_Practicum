## Formulas


### Net Operation Income(Noi)
+ For first year or last year
$$Noi_t = Sales Price_{t-1} * CapRate_{t-1} * TimeDiff_{t} \space (t \in [2, 3, 4, ......, n])$$

+ For years between the two sales(using cpi rate) 
$$Noi_t = Noi_{t-1} * (1 + CPI\space RATE_{t}) * TimeDiff_{t})$$

+ For years between two sales(using fixed average difference)
  
  $$Noi_t = Noi_{t-1} + fixed\space average\space difference_t * TimeDiff_{t})$$

### CPI Calculation

$$ CPI\space RATE_{date1 -> date2} = CPI_{date2} / CPI_{date1} - 1 $$

### Average difference

$$Fixed\space Average\space Difference = \frac{Noi_{n} - Noi_{1}}{n - 1} $$


### Cash Flow(CF)

$$if\space t = 1 \space \space CF = - SalesPrice $$
$$if\space t = n \space \space CF = SalesPrice + SalesCost + Noi$$

$$else \space \space CF_t= Noi_t$$


### Internal Return Rate


$$0 = \sum\limits_{i=1}^N\frac{P_i}{(1+rate)\frac{d_i - d_1}{365}}$$

Where
+ di = the ith, or last, payment date.

+ d1 = the 0th payment date.

+ Pi = the ith, or last, payment.