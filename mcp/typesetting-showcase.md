# A Small Model for Queueing and Capacity Planning

This note works through a reproducible capacity-planning example. It combines
inline mathematics, display equations, a comparison table, and executable code.
The numbers are illustrative rather than measurements from a production system.

## 1. Model and assumptions

Suppose jobs arrive at an average rate of $\lambda$ jobs per second and each
worker completes jobs at an average rate of $\mu$ jobs per second. With $c$
identical workers, the nominal utilization is

$$
\rho = \frac{\lambda}{c\mu}, \qquad 0 \leq \rho < 1.
$$

For an **M/M/1** approximation, the expected time in the system and the
expected number of jobs in the system are

$$
W = \frac{1}{\mu-\lambda}, \qquad
L = \lambda W = \frac{\lambda}{\mu-\lambda}.
$$

The single-worker formula is useful for intuition, but it does *not* model a
shared queue with multiple workers. The later comparison uses utilization only.

| Symbol | Meaning | Unit | Example |
|:---|:---|---:|---:|
| $\lambda$ | Mean arrival rate | jobs/s | 18 |
| $\mu$ | Mean service rate per worker | jobs/s | 5 |
| $c$ | Number of workers | workers | 4–8 |
| $\rho$ | Nominal utilization | fraction | $18/(5c)$ |

## 2. Capacity comparison

The following options use $\lambda=18$ jobs/s and $\mu=5$ jobs/s. The
**headroom** column is total service capacity less the arrival rate:
$h=c\mu-\lambda$.

| Workers $c$ | Capacity $c\mu$ (jobs/s) | Utilization $\rho$ | Headroom $h$ (jobs/s) | Assessment |
|---:|---:|---:|---:|:---|
| 4 | 20 | 90.0% | 2 | Little spare capacity |
| 5 | 25 | 72.0% | 7 | Moderate spare capacity |
| 6 | 30 | 60.0% | 12 | Comfortable baseline |
| 8 | 40 | 45.0% | 22 | Extra burst capacity |

If a planning rule limits utilization to $\rho_{\max}=0.70$, the smallest
whole-number worker count is

$$
c_{\min}
= \left\lceil \frac{\lambda}{\mu\rho_{\max}} \right\rceil
= \left\lceil \frac{18}{5(0.70)} \right\rceil
= 6.
$$

### Sensitivity to arrivals

For six workers, the utilization rises linearly with arrival rate:

$$
\rho(\lambda)=\frac{\lambda}{30}, \qquad
\frac{\partial\rho}{\partial\lambda}=\frac{1}{30}.
$$

An increase from 18 to 21 jobs/s therefore changes utilization from 60% to
70%. This calculation says nothing about tail latency, which also depends on
service-time variability and queue discipline.

## 3. Reproducible calculation

The Python example generates the rows above and checks that the capacity
constraint is satisfied. It uses only the standard library.

```python
from math import ceil

arrival_rate = 18.0       # jobs per second
service_rate = 5.0        # jobs per second, per worker
utilization_limit = 0.70

minimum_workers = ceil(arrival_rate / (service_rate * utilization_limit))

for workers in (4, 5, 6, 8):
    capacity = workers * service_rate
    utilization = arrival_rate / capacity
    headroom = capacity - arrival_rate
    print(f"{workers:>2}  {capacity:>5.1f}  {utilization:>6.1%}  {headroom:>5.1f}")

assert minimum_workers == 6
assert arrival_rate / (minimum_workers * service_rate) <= utilization_limit
```

Expected output:

```text
 4   20.0   90.0%    2.0
 5   25.0   72.0%    7.0
 6   30.0   60.0%   12.0
 8   40.0   45.0%   22.0
```

## 4. Interpretation

Six workers meet the 70% utilization rule at the assumed average load.
Before making a production decision, measure arrival bursts, processing-time
variation, and a latency percentile such as $p_{95}$. A useful follow-up is a
load test that records throughput and queue wait time for each worker count.
