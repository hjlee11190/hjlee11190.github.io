---
title: "[P2P] Constrained Graph Clustering"
collection: blogs
date: 2026-09-13
---

Hi! This is my first post on this blog :)

Some friends and I recently started a journal club called Peer to Paper (P2P), where we go through a math-related research paper from each of our fields once a week. You can find more info in this [GitHub repo](https://github.com/hongeun-im/P2P).

This week, one of our members covered **constrained graph clustering**, and below is my brief review of the topic. It might include some errors, but please excuse any mistakes...


### Graph Clustering
Graph clustering is generally about grouping nodes into separate clusters in a way that best reflects the edge weights of the graph. For the case of two clusters, this is often done using the **second eigenvector of the graph Laplacian**. 
The basic idea is that the Rayleigh quotient can be written as a weighted average of the Laplacian eigenvalues, and after excluding the trivial case, the minimum of the quotient is given by $\lambda_2$. However, the performance of standard spectral clustering can degrade rapidly as the probability of edges between different clusters increases.

### Constrained Graph Clustering

The main question addressed in the paper was:

> How can we perform clustering when we have additional information indicating that certain nodes should not be linked together?

The authors addressed this problem by formulating it as a **generalized eigenvalue problem**. They also compared how clustering performance changed across different methods as a function of $p$, the intra-cluster edge probability of a **must-link graph** $G$.

We can simplify the setting by defining the inter-cluster edge probability of a **cannot-link graph** $H$ using the same parameter $p$. As $p$ increases, the distinction between the clusters becomes stronger, lowering the value of the following ratio:

$$
\frac{\langle f, \Delta^G f \rangle}
     {\langle f, \Delta^H f \rangle}.
$$

![constrained graph clustering](/images/p2p/week1_constrained_graph_clustering.jpg)

### Remaining Questions
* Why do we need a negative self-loop? Wouldn't a positive self-loop also be sufficient if the only purpose is to make \(L\) invertible?
* Could we formulate the problem using a single graph by modifying the edge weights (probably something like assigning more negative weights) instead of representing the constraints using a separate graph?