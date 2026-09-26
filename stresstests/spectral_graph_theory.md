# Spectral Graph Theory: Laplacians, Eigenmodes, Random Walks, and Graph Diffusion

> A compact but mathematically serious introduction to spectral graph theory, with notation, derivations, examples, tables, and low-level implementations.

---

## 1. Overview

Spectral graph theory studies a graph through the eigenvalues and eigenvectors of matrices associated with it.

Given an undirected weighted graph

\[
G=(V,E,W),
\]

with vertices

\[
V=\{1,2,\dots,n\},
\]

we encode the graph using a weighted adjacency matrix

\[
A\in\mathbb{R}^{n\times n},
\]

where

\[
A_{ij}=
\begin{cases}
w_{ij}, & (i,j)\in E,\\[4pt]
0, & \text{otherwise}.
\end{cases}
\]

For an undirected graph,

\[
A=A^\top.
\]

The weighted degree of node \(i\) is

\[
d_i=\sum_{j=1}^n A_{ij},
\]

and the degree matrix is

\[
D=\operatorname{diag}(d_1,d_2,\dots,d_n).
\]

The central object is the **graph Laplacian**:

\[
\boxed{L=D-A}
\]

The spectrum of \(L\),

\[
0=\lambda_1\le \lambda_2\le \cdots \le \lambda_n,
\]

reveals connectivity, clustering structure, diffusion behaviour, smooth graph signals, and random-walk dynamics.

---

# 2. Notation

| Symbol | Meaning |
|---|---|
| \(G=(V,E,W)\) | Weighted undirected graph |
| \(n\) | Number of vertices |
| \(A\) | Adjacency matrix |
| \(D\) | Degree matrix |
| \(L=D-A\) | Combinatorial graph Laplacian |
| \(L_{\mathrm{sym}}\) | Symmetric normalized Laplacian |
| \(L_{\mathrm{rw}}\) | Random-walk Laplacian |
| \(P=D^{-1}A\) | Random-walk transition matrix |
| \(x\in\mathbb{R}^n\) | Scalar-valued graph signal |
| \(\lambda_k\) | \(k\)-th Laplacian eigenvalue |
| \(u_k\) | Eigenvector corresponding to \(\lambda_k\) |
| \(U\) | Matrix of eigenvectors |
| \(\Lambda\) | Diagonal matrix of eigenvalues |
| \(\mathcal{E}(x)\) | Dirichlet energy of signal \(x\) |
| \(e^{-tL}\) | Heat kernel / diffusion operator |

---

# 3. The Graph Laplacian

The combinatorial Laplacian is

\[
L=D-A.
\]

Elementwise,

\[
L_{ij}
=
\begin{cases}
d_i, & i=j,\\
-A_{ij}, & i\neq j.
\end{cases}
\]

For example, consider the weighted graph

\[
1 \xleftrightarrow{2} 2
\xleftrightarrow{1} 3,
\qquad
1 \xleftrightarrow{1} 3.
\]

Its adjacency matrix is

\[
A=
\begin{bmatrix}
0 & 2 & 1\\
2 & 0 & 1\\
1 & 1 & 0
\end{bmatrix}.
\]

The degrees are

\[
d_1=3,\qquad d_2=3,\qquad d_3=2.
\]

Therefore,

\[
D=
\begin{bmatrix}
3&0&0\\
0&3&0\\
0&0&2
\end{bmatrix},
\]

and

\[
L=D-A
=
\begin{bmatrix}
3&-2&-1\\
-2&3&-1\\
-1&-1&2
\end{bmatrix}.
\]

---

# 4. Fundamental Quadratic Form

One of the most important identities in spectral graph theory is

\[
\boxed{
x^\top Lx
=
\frac12
\sum_{i=1}^n
\sum_{j=1}^n
A_{ij}(x_i-x_j)^2
}
\]

For an undirected graph, this is equivalently

\[
x^\top Lx
=
\sum_{(i,j)\in E}
w_{ij}(x_i-x_j)^2.
\]

This quantity is called the **Dirichlet energy**:

\[
\mathcal{E}(x)=x^\top Lx.
\]

It measures how rapidly a graph signal changes across connected vertices.

If neighbouring nodes have similar values,

\[
x_i\approx x_j,
\]

then

\[
(x_i-x_j)^2\approx 0,
\]

and the energy is small.

---

## 4.1 Derivation

Start with

\[
x^\top Lx=x^\top(D-A)x.
\]

Hence

\[
x^\top Lx
=
x^\top Dx-x^\top Ax.
\]

The first term is

\[
x^\top Dx
=
\sum_i d_i x_i^2.
\]

Since

\[
d_i=\sum_j A_{ij},
\]

we have

\[
x^\top Dx
=
\sum_{i,j}A_{ij}x_i^2.
\]

Similarly,

\[
x^\top Ax
=
\sum_{i,j}A_{ij}x_ix_j.
\]

Therefore,

\[
x^\top Lx
=
\sum_{i,j}A_{ij}x_i^2
-
\sum_{i,j}A_{ij}x_ix_j.
\]

Using symmetry \(A_{ij}=A_{ji}\),

\[
\sum_{i,j}A_{ij}x_i^2
=
\frac12
\sum_{i,j}
A_{ij}(x_i^2+x_j^2).
\]

Thus,

\[
x^\top Lx
=
\frac12
\sum_{i,j}
A_{ij}
\left(
x_i^2+x_j^2-2x_ix_j
\right),
\]

so

\[
\boxed{
x^\top Lx
=
\frac12
\sum_{i,j}
A_{ij}(x_i-x_j)^2
}
\]

---

# 5. Positive Semidefiniteness

Because every term

\[
A_{ij}(x_i-x_j)^2
\]

is nonnegative whenever

\[
A_{ij}\ge 0,
\]

we obtain

\[
x^\top Lx\ge 0
\]

for every

\[
x\in\mathbb{R}^n.
\]

Therefore,

\[
\boxed{L\succeq 0}
\]

and every eigenvalue satisfies

\[
\lambda_k\ge 0.
\]

---

# 6. The Zero Eigenvalue

Let

\[
\mathbf{1}
=
\begin{bmatrix}
1\\
1\\
\vdots\\
1
\end{bmatrix}.
\]

Then

\[
L\mathbf{1}
=
(D-A)\mathbf{1}.
\]

But

\[
A\mathbf{1}
=
\begin{bmatrix}
d_1\\
d_2\\
\vdots\\
d_n
\end{bmatrix}
=
D\mathbf{1}.
\]

Therefore,

\[
\boxed{
L\mathbf{1}=0
}
\]

and hence

\[
\lambda_1=0.
\]

More strongly:

\[
\boxed{
\text{Multiplicity of eigenvalue }0
=
\text{number of connected components of }G.
}
\]

If the graph is connected, then

\[
\lambda_1=0
\]

has multiplicity one.

---

# 7. The Spectral Decomposition

Because \(L\) is real and symmetric, the spectral theorem guarantees

\[
L=U\Lambda U^\top,
\]

where

\[
U=
\begin{bmatrix}
u_1 & u_2 & \cdots & u_n
\end{bmatrix}
\]

is orthogonal,

\[
U^\top U=I,
\]

and

\[
\Lambda
=
\operatorname{diag}
(\lambda_1,\lambda_2,\dots,\lambda_n).
\]

Each eigenvector satisfies

\[
Lu_k=\lambda_k u_k.
\]

The vectors

\[
u_1,\dots,u_n
\]

form an orthonormal basis of \(\mathbb{R}^n\).

Thus any graph signal \(x\) can be written as

\[
x
=
\sum_{k=1}^n
\hat{x}_k u_k,
\]

where

\[
\boxed{
\hat{x}_k=u_k^\top x
}
\]

is the graph Fourier coefficient of \(x\).

---

# 8. Graph Fourier Transform

The ordinary Fourier transform decomposes a signal into sinusoidal frequencies.

For graphs, the Laplacian eigenvectors play the role of generalized frequency modes.

Define

\[
\hat{x}=U^\top x.
\]

Then the inverse graph Fourier transform is

\[
x=U\hat{x}.
\]

Thus,

\[
\boxed{
\hat{x}=U^\top x,
\qquad
x=U\hat{x}.
}
\]

---

## 8.1 Why Eigenvalues Behave Like Frequencies

Recall that

\[
Lu_k=\lambda_k u_k.
\]

Therefore,

\[
u_k^\top L u_k
=
\lambda_k u_k^\top u_k
=
\lambda_k.
\]

But

\[
u_k^\top Lu_k
=
\sum_{(i,j)\in E}
w_{ij}
\left(
u_k(i)-u_k(j)
\right)^2.
\]

Hence large \(\lambda_k\) means the eigenvector varies strongly across adjacent nodes.

So:

| Laplacian Eigenvalue | Interpretation |
|---:|---|
| \(\lambda_1=0\) | Constant / DC component |
| Small \(\lambda_k\) | Smooth variation across graph |
| Intermediate \(\lambda_k\) | Medium-scale graph structure |
| Large \(\lambda_k\) | Rapid oscillation across edges |

---

# 9. The Fiedler Value and Fiedler Vector

For a connected graph,

\[
0=\lambda_1 < \lambda_2.
\]

The second-smallest eigenvalue

\[
\boxed{\lambda_2}
\]

is called the **algebraic connectivity** or **Fiedler value**.

Its eigenvector

\[
\boxed{u_2}
\]

is called the **Fiedler vector**.

The magnitude of \(\lambda_2\) quantifies how strongly connected the graph is.

A small value of

\[
\lambda_2
\]

often indicates a graph with a weak bottleneck.

---

## 9.1 Variational Characterization

The Courant–Fischer theorem gives

\[
\lambda_2
=
\min_{\substack{x\neq 0\\x^\top \mathbf{1}=0}}
\frac{x^\top Lx}{x^\top x}.
\]

Equivalently,

\[
\boxed{
\lambda_2
=
\min_{\substack{\|x\|_2=1\\x^\top \mathbf{1}=0}}
x^\top Lx
}
\]

Thus \(u_2\) is the smoothest nonconstant signal on the graph.

This is precisely why its sign pattern is useful for spectral graph partitioning.

---

# 10. Spectral Clustering

A simple two-way partition may be created using the Fiedler vector:

\[
C_1=\{i:u_2(i)\ge 0\},
\]

\[
C_2=\{i:u_2(i)<0\}.
\]

For \(k\)-way spectral clustering:

1. Construct \(L\) or \(L_{\mathrm{sym}}\).
2. Compute the first \(k\) nontrivial eigenvectors.
3. Form

\[
Z=
\begin{bmatrix}
u_1 & u_2 & \cdots & u_k
\end{bmatrix}.
\]

4. Represent node \(i\) by row

\[
z_i^\top.
\]

5. Run \(k\)-means on

\[
\{z_1,\dots,z_n\}.
\]

The graph is therefore embedded into a low-dimensional Euclidean space.

---

# 11. Normalized Laplacians

The combinatorial Laplacian can behave poorly when node degrees vary widely.

Two standard normalizations are used.

## 11.1 Symmetric Normalized Laplacian

\[
\boxed{
L_{\mathrm{sym}}
=
D^{-1/2}LD^{-1/2}
=
I-D^{-1/2}AD^{-1/2}
}
\]

## 11.2 Random-Walk Laplacian

\[
\boxed{
L_{\mathrm{rw}}
=
D^{-1}L
=
I-D^{-1}A
}
\]

Define

\[
P=D^{-1}A.
\]

Then

\[
P_{ij}
=
\frac{A_{ij}}{d_i}
\]

is a row-stochastic matrix:

\[
\sum_j P_{ij}=1.
\]

Hence,

\[
\boxed{
L_{\mathrm{rw}}=I-P.
}
\]

---

# 12. Random Walk Interpretation

Let

\[
p^{(t)}
\]

be a row vector giving a probability distribution over vertices at time \(t\).

Then

\[
p^{(t+1)}
=
p^{(t)}P.
\]

After \(t\) steps,

\[
\boxed{
p^{(t)}
=
p^{(0)}P^t.
}
\]

For a connected, non-bipartite undirected graph, the random walk converges to

\[
\pi_i
=
\frac{d_i}{\sum_j d_j}.
\]

Thus high-degree nodes receive more stationary probability mass.

---

# 13. Heat Diffusion on Graphs

Suppose \(x(t)\in\mathbb{R}^n\) represents temperature, concentration, activation, or information distributed over graph vertices.

Continuous diffusion is governed by

\[
\boxed{
\frac{dx}{dt}
=
-Lx
}
\]

with initial condition

\[
x(0)=x_0.
\]

The solution is

\[
\boxed{
x(t)
=
e^{-tL}x_0.
}
\]

Since

\[
L=U\Lambda U^\top,
\]

we have

\[
e^{-tL}
=
Ue^{-t\Lambda}U^\top,
\]

where

\[
e^{-t\Lambda}
=
\operatorname{diag}
\left(
e^{-t\lambda_1},
e^{-t\lambda_2},
\dots,
e^{-t\lambda_n}
\right).
\]

Therefore,

\[
x(t)
=
\sum_{k=1}^n
e^{-t\lambda_k}
\hat{x}_k u_k.
\]

High-frequency modes decay faster because

\[
\lambda_k\gg 0
\quad\Longrightarrow\quad
e^{-t\lambda_k}\to 0
\]

rapidly.

---

# 14. Graph Filtering

A spectral graph filter is defined by a scalar transfer function

\[
h(\lambda).
\]

Then

\[
h(L)
=
Uh(\Lambda)U^\top,
\]

where

\[
h(\Lambda)
=
\operatorname{diag}
(
h(\lambda_1),\dots,h(\lambda_n)
).
\]

Applied to a graph signal,

\[
\boxed{
y=h(L)x.
}
\]

A heat-kernel low-pass filter uses

\[
h(\lambda)=e^{-t\lambda}.
\]

Therefore,

\[
y=e^{-tL}x.
\]

A polynomial graph filter has the form

\[
h(L)
=
\sum_{r=0}^K
\alpha_r L^r.
\]

This avoids explicit eigendecomposition.

---

# 15. Connection to Graph Neural Networks

Many graph neural networks can be interpreted as approximate graph filters.

A simplified message-passing operation is

\[
H^{(\ell+1)}
=
\sigma
\left(
\widetilde{D}^{-1/2}
\widetilde{A}
\widetilde{D}^{-1/2}
H^{(\ell)}
W^{(\ell)}
\right),
\]

where

\[
\widetilde{A}=A+I,
\]

\[
\widetilde{D}_{ii}
=
\sum_j \widetilde{A}_{ij}.
\]

The propagation operator

\[
\widetilde{D}^{-1/2}
\widetilde{A}
\widetilde{D}^{-1/2}
\]

acts as a form of neighborhood smoothing.

Repeated multiplication suppresses high-frequency graph components, which explains the phenomenon of **over-smoothing**:

\[
H^{(\ell)}
\to
\text{low-dimensional smooth subspace}
\]

as

\[
\ell\to\infty.
\]

---

# 16. Discrete-Time Diffusion Stability

A forward Euler discretization of

\[
\frac{dx}{dt}=-Lx
\]

with step size \(\Delta t\) gives

\[
x_{t+1}
=
x_t-\Delta t Lx_t.
\]

Therefore,

\[
\boxed{
x_{t+1}
=
(I-\Delta t L)x_t.
}
\]

For numerical stability we require

\[
|1-\Delta t\lambda_k|\le 1
\]

for all \(k\).

Thus,

\[
0\le \Delta t\lambda_k\le 2.
\]

Since the largest eigenvalue dominates,

\[
\boxed{
\Delta t
\le
\frac{2}{\lambda_{\max}(L)}.
}
\]

---

# 17. Worked Example

Consider

\[
A=
\begin{bmatrix}
0&1&1&0\\
1&0&1&0\\
1&1&0&1\\
0&0&1&0
\end{bmatrix}.
\]

The degree matrix is

\[
D=
\begin{bmatrix}
2&0&0&0\\
0&2&0&0\\
0&0&3&0\\
0&0&0&1
\end{bmatrix}.
\]

Therefore,

\[
L=
\begin{bmatrix}
2&-1&-1&0\\
-1&2&-1&0\\
-1&-1&3&-1\\
0&0&-1&1
\end{bmatrix}.
\]

Take the graph signal

\[
x=
\begin{bmatrix}
1\\
1\\
0\\
0
\end{bmatrix}.
\]

Then

\[
Lx
=
\begin{bmatrix}
1\\
1\\
-2\\
0
\end{bmatrix}.
\]

The Dirichlet energy is

\[
x^\top Lx
=
\begin{bmatrix}
1&1&0&0
\end{bmatrix}
\begin{bmatrix}
1\\
1\\
-2\\
0
\end{bmatrix}
=2.
\]

Checking edgewise,

\[
\mathcal{E}(x)
=
(1-1)^2
+
(1-0)^2
+
(1-0)^2
+
(0-0)^2.
\]

Hence

\[
\boxed{
\mathcal{E}(x)=2.
}
\]

---

# 18. Matrix Comparison

| Matrix | Definition | Symmetric? | Main interpretation |
|---|---|---:|---|
| \(A\) | Adjacency matrix | Yes, for undirected graphs | Edge connectivity |
| \(D\) | \(\operatorname{diag}(d_i)\) | Yes | Node degree scaling |
| \(L\) | \(D-A\) | Yes | Smoothness / energy |
| \(L_{\mathrm{sym}}\) | \(I-D^{-1/2}AD^{-1/2}\) | Yes | Degree-normalized geometry |
| \(L_{\mathrm{rw}}\) | \(I-D^{-1}A\) | Generally no | Random-walk dynamics |
| \(P\) | \(D^{-1}A\) | Generally no | Markov transition operator |
| \(e^{-tL}\) | Matrix exponential | Yes | Heat diffusion kernel |

---

# 19. Computational Complexity

For dense matrices, eigendecomposition is expensive.

| Operation | Dense Complexity | Sparse Graph Complexity |
|---|---:|---:|
| Construct \(A\) | \(O(n^2)\) | \(O(|E|)\) |
| Construct \(L\) | \(O(n^2)\) | \(O(|E|)\) |
| Dense eigendecomposition | \(O(n^3)\) | — |
| Sparse matrix-vector multiply | \(O(n^2)\) | \(O(|E|)\) |
| Lanczos for \(k\) eigenpairs | — | Roughly \(O(k|E|)\) per iteration regime |
| One diffusion Euler step | \(O(n^2)\) | \(O(|E|)\) |

For very large graphs, algorithms avoid explicitly forming dense matrices.

---

# 20. Low-Level Implementation in C

The following program constructs a dense Laplacian from an adjacency matrix and computes

\[
y=Lx.
\]

```c
#include <stdio.h>
#include <stddef.h>

#define N 4

void build_laplacian(
    const double A[N][N],
    double L[N][N]
) {
    for (size_t i = 0; i < N; ++i) {
        double degree = 0.0;

        for (size_t j = 0; j < N; ++j) {
            degree += A[i][j];
        }

        for (size_t j = 0; j < N; ++j) {
            if (i == j) {
                L[i][j] = degree - A[i][j];
            } else {
                L[i][j] = -A[i][j];
            }
        }
    }
}

void matvec(
    const double M[N][N],
    const double x[N],
    double y[N]
) {
    for (size_t i = 0; i < N; ++i) {
        double acc = 0.0;

        for (size_t j = 0; j < N; ++j) {
            acc += M[i][j] * x[j];
        }

        y[i] = acc;
    }
}

double dot(
    const double a[N],
    const double b[N]
) {
    double result = 0.0;

    for (size_t i = 0; i < N; ++i) {
        result += a[i] * b[i];
    }

    return result;
}

int main(void) {
    const double A[N][N] = {
        {0.0, 1.0, 1.0, 0.0},
        {1.0, 0.0, 1.0, 0.0},
        {1.0, 1.0, 0.0, 1.0},
        {0.0, 0.0, 1.0, 0.0}
    };

    const double x[N] = {
        1.0,
        1.0,
        0.0,
        0.0
    };

    double L[N][N];
    double y[N];

    build_laplacian(A, L);
    matvec(L, x, y);

    printf("Lx = [");

    for (size_t i = 0; i < N; ++i) {
        printf("%s%.3f", i == 0 ? "" : ", ", y[i]);
    }

    printf("]\\n");

    const double energy = dot(x, y);

    printf("x^T L x = %.3f\\n", energy);

    return 0;
}
```

Expected output:

```text
Lx = [1.000, 1.000, -2.000, 0.000]
x^T L x = 2.000
```

---

# 21. Sparse Laplacian Multiplication in C

For large graphs, storing the full matrix is wasteful.

Instead, represent edges as a compact edge list.

For each undirected edge

\[
(i,j,w),
\]

the Laplacian contribution is

\[
y_i \mathrel{+}= w(x_i-x_j),
\]

\[
y_j \mathrel{+}= w(x_j-x_i).
\]

```c
#include <stdio.h>
#include <stddef.h>

typedef struct {
    size_t u;
    size_t v;
    double weight;
} Edge;

void laplacian_matvec(
    size_t n,
    const Edge *edges,
    size_t m,
    const double *x,
    double *y
) {
    for (size_t i = 0; i < n; ++i) {
        y[i] = 0.0;
    }

    for (size_t e = 0; e < m; ++e) {
        const size_t u = edges[e].u;
        const size_t v = edges[e].v;
        const double w = edges[e].weight;

        const double diff = x[u] - x[v];

        y[u] += w * diff;
        y[v] -= w * diff;
    }
}

int main(void) {
    const size_t n = 4;

    const Edge edges[] = {
        {0, 1, 1.0},
        {0, 2, 1.0},
        {1, 2, 1.0},
        {2, 3, 1.0}
    };

    const size_t m = sizeof(edges) / sizeof(edges[0]);

    const double x[] = {
        1.0,
        1.0,
        0.0,
        0.0
    };

    double y[4];

    laplacian_matvec(
        n,
        edges,
        m,
        x,
        y
    );

    for (size_t i = 0; i < n; ++i) {
        printf("y[%zu] = %.3f\\n", i, y[i]);
    }

    return 0;
}
```

This algorithm requires

\[
O(|E|)
\]

time and

\[
O(n+|E|)
\]

memory.

---

# 22. Power Iteration for the Largest Laplacian Eigenvalue

The largest eigenvalue

\[
\lambda_{\max}(L)
\]

is useful for numerical stability bounds.

A simple power iteration updates

\[
v_{k+1}
=
\frac{Lv_k}{\|Lv_k\|_2}.
\]

The Rayleigh quotient

\[
\rho(v)
=
\frac{v^\top Lv}{v^\top v}
\]

approaches the dominant eigenvalue.

```c
#include <math.h>
#include <stddef.h>

double dot_product(
    const double *a,
    const double *b,
    size_t n
) {
    double s = 0.0;

    for (size_t i = 0; i < n; ++i) {
        s += a[i] * b[i];
    }

    return s;
}

double l2_norm(
    const double *x,
    size_t n
) {
    return sqrt(dot_product(x, x, n));
}

void normalize(
    double *x,
    size_t n
) {
    const double norm = l2_norm(x, n);

    if (norm == 0.0) {
        return;
    }

    for (size_t i = 0; i < n; ++i) {
        x[i] /= norm;
    }
}
```

A sparse Laplacian-vector multiplication routine can then be embedded into the iteration.

---

# 23. Rust Implementation of a Diffusion Step

The explicit Euler update is

\[
x^{(t+1)}
=
x^{(t)}
-
\Delta t Lx^{(t)}.
\]

For a sparse graph:

```rust
#[derive(Clone, Copy)]
struct Edge {
    u: usize,
    v: usize,
    weight: f64,
}

fn laplacian_matvec(
    n: usize,
    edges: &[Edge],
    x: &[f64],
) -> Vec<f64> {
    let mut y = vec![0.0; n];

    for edge in edges {
        let diff = x[edge.u] - x[edge.v];

        y[edge.u] += edge.weight * diff;
        y[edge.v] -= edge.weight * diff;
    }

    y
}

fn diffusion_step(
    n: usize,
    edges: &[Edge],
    x: &[f64],
    dt: f64,
) -> Vec<f64> {
    let lx = laplacian_matvec(n, edges, x);

    x.iter()
        .zip(lx.iter())
        .map(|(xi, lxi)| xi - dt * lxi)
        .collect()
}

fn main() {
    let edges = vec![
        Edge { u: 0, v: 1, weight: 1.0 },
        Edge { u: 0, v: 2, weight: 1.0 },
        Edge { u: 1, v: 2, weight: 1.0 },
        Edge { u: 2, v: 3, weight: 1.0 },
    ];

    let mut x = vec![1.0, 0.0, 0.0, 0.0];

    let dt = 0.1;

    for _ in 0..20 {
        x = diffusion_step(
            4,
            &edges,
            &x,
            dt,
        );
    }

    println!("{:?}", x);
}
```

---

# 24. Numerical Interpretation of Diffusion

Suppose

\[
x(0)
=
\begin{bmatrix}
1\\
0\\
0\\
0
\end{bmatrix}.
\]

Initially all mass is concentrated at node \(1\).

As

\[
t\to\infty,
\]

the solution

\[
x(t)=e^{-tL}x(0)
\]

approaches the projection of \(x(0)\) onto the nullspace of \(L\).

For a connected graph,

\[
\operatorname{null}(L)
=
\operatorname{span}\{\mathbf{1}\}.
\]

Hence,

\[
x(t)
\to
\frac{\mathbf{1}^\top x(0)}{n}
\mathbf{1}.
\]

If total mass is one,

\[
\mathbf{1}^\top x(0)=1,
\]

then

\[
\boxed{
x(t)
\to
\frac1n\mathbf{1}.
}
\]

Thus heat diffusion on the combinatorial Laplacian converges to a uniform temperature.

---

# 25. Rayleigh Quotient

For nonzero \(x\),

\[
\boxed{
R_L(x)
=
\frac{x^\top Lx}{x^\top x}
}
\]

The Rayleigh quotient measures the graph-frequency content of \(x\).

Because

\[
L=U\Lambda U^\top,
\]

write

\[
x=\sum_k \alpha_k u_k.
\]

Then

\[
x^\top Lx
=
\sum_k
\lambda_k \alpha_k^2,
\]

while

\[
x^\top x
=
\sum_k
\alpha_k^2.
\]

Therefore,

\[
R_L(x)
=
\frac{
\sum_k
\lambda_k\alpha_k^2
}{
\sum_k
\alpha_k^2
}.
\]

This is a weighted average of Laplacian eigenvalues.

Hence,

\[
\lambda_1
\le
R_L(x)
\le
\lambda_n.
\]

---

# 26. Cheeger-Type Intuition

For a vertex subset

\[
S\subset V,
\]

define its volume

\[
\operatorname{vol}(S)
=
\sum_{i\in S}d_i.
\]

Let

\[
\bar S=V\setminus S.
\]

The edge boundary is

\[
\partial S
=
\{(i,j)\in E:i\in S,\ j\in \bar S\}.
\]

A normalized cut quantity is

\[
\phi(S)
=
\frac{
\sum_{i\in S,j\in\bar S}w_{ij}
}{
\min(
\operatorname{vol}(S),
\operatorname{vol}(\bar S)
)
}.
\]

The graph conductance is

\[
\phi_G
=
\min_S \phi(S).
\]

Cheeger-type inequalities connect conductance to spectral quantities such as \(\lambda_2\), roughly of the form

\[
\frac{\lambda_2}{2}
\lesssim
\phi_G
\lesssim
\sqrt{2\lambda_2},
\]

for the appropriate normalized Laplacian.

This establishes a deep bridge between:

- combinatorial bottlenecks,
- optimization,
- random walks,
- and Laplacian eigenvalues.

---

# 27. Spectral Gap and Mixing

For a random walk transition matrix \(P\),

\[
P=D^{-1}A.
\]

Let its eigenvalues be

\[
1=\mu_1>\mu_2\ge \cdots.
\]

The quantity

\[
\boxed{
1-|\mu_2|
}
\]

is often called a spectral gap.

A larger gap generally implies faster convergence of the Markov chain toward stationarity.

Since

\[
L_{\mathrm{rw}}=I-P,
\]

their eigenvalues satisfy

\[
\lambda_k^{(\mathrm{rw})}
=
1-\mu_k.
\]

Thus random-walk convergence is directly encoded in the Laplacian spectrum.

---

# 28. Discrete Graph Gradient

For an oriented edge

\[
e=(i,j),
\]

define the incidence matrix

\[
B\in\mathbb{R}^{|E|\times n}
\]

so that the row corresponding to \(e\) contains

\[
B_{e,i}=1,
\qquad
B_{e,j}=-1.
\]

Then

\[
Bx
\]

contains the edgewise differences

\[
x_i-x_j.
\]

For weighted graphs, let

\[
W_E
=
\operatorname{diag}(w_e).
\]

Then the graph Laplacian can be written as

\[
\boxed{
L
=
B^\top W_E B.
}
\]

Therefore,

\[
x^\top Lx
=
x^\top B^\top W_E Bx
=
(Bx)^\top W_E(Bx).
\]

This is the graph analogue of

\[
\int
\|\nabla f(x)\|^2 dx
\]

in continuous calculus.

---

# 29. Continuous vs Graph Operators

| Continuous Object | Graph Analogue |
|---|---|
| Function \(f(x)\) | Graph signal \(x_i\) |
| Gradient \(\nabla f\) | Incidence operation \(Bx\) |
| Dirichlet energy \(\int \|\nabla f\|^2\) | \(x^\top Lx\) |
| Laplacian \(-\nabla^2\) | Graph Laplacian \(L\) |
| Fourier basis | Laplacian eigenvectors |
| Frequency \(\omega^2\) | Eigenvalue \(\lambda_k\) |
| Heat equation \(\partial_t f=\Delta f\) | \(dx/dt=-Lx\) |
| Heat kernel | \(e^{-tL}\) |

---

# 30. Why This Framework Is Powerful

The same matrix

\[
L=D-A
\]

simultaneously encodes:

1. graph connectivity,
2. smoothness of node signals,
3. graph partitions,
4. random walks,
5. diffusion,
6. generalized Fourier analysis,
7. numerical PDE analogues,
8. graph embeddings,
9. message passing,
10. clustering geometry.

This is unusual: a single algebraic object links discrete mathematics, probability, numerical analysis, optimization, machine learning, and dynamical systems.

---

# 31. Summary

The graph Laplacian is

\[
\boxed{
L=D-A
}
\]

and satisfies

\[
L\succeq 0.
\]

Its quadratic form is

\[
\boxed{
x^\top Lx
=
\frac12
\sum_{i,j}
A_{ij}(x_i-x_j)^2.
}
\]

Its eigendecomposition is

\[
\boxed{
L=U\Lambda U^\top.
}
\]

The graph Fourier transform is

\[
\boxed{
\hat{x}=U^\top x.
}
\]

The second eigenvalue

\[
\lambda_2
\]

measures algebraic connectivity, while its eigenvector is used in spectral partitioning.

Diffusion obeys

\[
\boxed{
\frac{dx}{dt}=-Lx,
\qquad
x(t)=e^{-tL}x(0).
}
\]

Graph filtering is expressed as

\[
\boxed{
y=h(L)x.
}
\]

The incidence representation is

\[
\boxed{
L=B^\top W_E B.
}
\]

Together, these identities form the foundation of modern spectral methods on graphs.

---

# 32. Suggested Exercises

1. Compute \(L\) for a path graph with five vertices.
2. Show directly that every row of \(L\) sums to zero.
3. Verify numerically that \(L\succeq0\).
4. Compute the Fiedler vector of a graph consisting of two dense clusters joined by one weak edge.
5. Simulate

   \[
   x_{t+1}
   =
   (I-\Delta tL)x_t
   \]

   for multiple values of \(\Delta t\).

6. Demonstrate instability when

   \[
   \Delta t>\frac{2}{\lambda_{\max}(L)}.
   \]

7. Implement a polynomial graph filter

   \[
   y=
   \alpha_0x
   +
   \alpha_1Lx
   +
   \alpha_2L^2x.
   \]

8. Compare clustering obtained from:
   - raw adjacency rows,
   - the Fiedler vector,
   - the first three normalized-Laplacian eigenvectors.

---

## End
