---
title: "[P2P] Matrix-weighted Consensus"
collection: blogs
date: 2026-09-15
excerpt: "Finding a single representative value in a graph"
---

This is the concept I learned in the [P2P](https://github.com/hongeun-im/P2P) session this week. Special thanks to [Woojin Shin](https://adobby77.github.io/) -- the contents below are all based on his notes and explanations.

Suppose there are multiple sensors recording temperature in a single area. **How could we find a representative value in this sensor network while the value measured by each sensor varies?** This kind of situation can arise when we want to answer questions like "What's the weather like in Seoul?" or "Which direction should this robot move in?" 

### Reaching Consensus
The core idea we can use is:

> The rate of change of each unit's state is governed by the sum of its relative states w.r.t. neighboring units.

So, the greater the differences between neighboring nodes, the more updates occur. This kind of basic framing is especially reasonable because, in many situations nodes can only access information from their neighbors, not global information. A system can reach consensus iff its graph is connected.

![matrix-weighted consensus](/images/p2p/week2_matrix-weighted_consensus(0).png){: width="60%" style="display:block; margin:0 auto;"}

Surprisingly, with these dynamics, the nodes converge to the average value of the initial distribution.
* The centroid (= average of the initial state) remains constant at any time point during convergence.
* The centroid is an orthogonal projection of the initial state onto the agreement space (i.e., $\operatorname{span}\lbrace\mathbb{1}\rbrace$).

![matrix-weighted consensus](/images/p2p/week2_matrix-weighted_consensus(1).jpg)

### Matrix-weighted Consensus
An advanced version of this framework can be considered when **the weights are not scalars, but matrices**. Here, we assume the graph to be undirected, with symmetric, positive semi-definite matrix weights. We can think of this situation when nodes contain multiple types of information, such as $\mathbb{x}=[t_1, h_1]^T$.

The consensus protocol takes almost the same form as the previous one in terms of convergence stability (global asymptotic convergence), the consensus value, and the invariance of the average. Once the initial state is determined, the equilibrium is unique.

![matrix-weighted consensus](/images/p2p/week2_matrix-weighted_consensus(2).jpg)

### Remaining Questions
* Is there any condition on the network topology that makes consensus much faster or more efficient?
* Are there any different forms of assumptions for the update dynamics?