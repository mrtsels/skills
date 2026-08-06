---
name: latex-drawing-guide
description: "Draw publication-quality scientific diagrams in LaTeX — TikZ fundamentals, PGFPlots, reusable figure collections (neural networks, Bayesian graphs, tensors, time series), and TikZ library reference."
metadata:
  openclaw:
    emoji: "🎨"
    category: "writing"
    subcategory: "latex"
    keywords: ["LaTeX typesetting", "LaTeX figure insertion", "LaTeX custom style", "scientific figure creation"]
    source: "https://github.com/xinychen/awesome-latex-drawing"
---

# LaTeX Drawing Guide

## Overview

Publication-quality figures are a critical component of scientific papers. While external tools like matplotlib or Inkscape can produce good results, drawing figures directly in LaTeX using TikZ and PGFPlots offers unique advantages: figures share the same fonts and styling as the document, scale perfectly at any resolution, and remain fully version-controllable as plain text.

This guide draws from the awesome-latex-drawing repository (2,000+ stars), which provides 30+ complete examples of LaTeX-drawn figures covering Bayesian networks, neural network architectures, function plots, tensor diagrams, and machine learning frameworks. The techniques here apply broadly to any discipline that needs diagrams, flowcharts, or data plots embedded in LaTeX documents.

Learning TikZ has a steep initial curve, but the investment pays off substantially for researchers who publish frequently. Once you build a library of reusable components, creating new figures becomes fast and consistent.

## TikZ Fundamentals

### Basic Setup

```latex
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning, calc, shapes.geometric, fit}
```

### Coordinate System and Basic Shapes

```latex
\begin{tikzpicture}
  % Rectangle
  \draw[fill=blue!20, rounded corners] (0,0) rectangle (3,2);

  % Circle
  \draw[fill=red!20] (5,1) circle (1cm);

  % Arrow
  \draw[-{Stealth[length=3mm]}, thick] (3.2,1) -- (3.8,1);

  % Text node
  \node at (1.5,1) {Input};
  \node at (5,1) {Output};
\end{tikzpicture}
```

### Node-Based Diagrams

Nodes are the building blocks of most scientific diagrams:

```latex
\begin{tikzpicture}[
  block/.style={
    rectangle, draw, fill=blue!10,
    minimum width=2.5cm, minimum height=1cm,
    rounded corners, font=\small
  },
  arrow/.style={-{Stealth[length=2.5mm]}, thick}
]
  \node[block] (input) {Data Input};
  \node[block, right=2cm of input] (process) {Processing};
  \node[block, right=2cm of process] (output) {Results};

  \draw[arrow] (input) -- (process);
  \draw[arrow] (process) -- (output);
\end{tikzpicture}
```

## Neural Network Diagrams

### Fully Connected Layer

```latex
\begin{tikzpicture}[
  neuron/.style={circle, draw, fill=orange!30, minimum size=8mm},
  conn/.style={->, gray!70}
]
  % Input layer
  \foreach \i in {1,...,3}
    \node[neuron] (I\i) at (0, -\i*1.2) {$x_{\i}$};

  % Hidden layer
  \foreach \j in {1,...,4}
    \node[neuron, fill=blue!20] (H\j) at (3, -\j*1.2+0.6) {$h_{\j}$};

  % Output layer
  \foreach \k in {1,...,2}
    \node[neuron, fill=green!20] (O\k) at (6, -\k*1.2-0.6) {$y_{\k}$};

  % Connections
  \foreach \i in {1,...,3}
    \foreach \j in {1,...,4}
      \draw[conn] (I\i) -- (H\j);
  \foreach \j in {1,...,4}
    \foreach \k in {1,...,2}
      \draw[conn] (H\j) -- (O\k);

  % Labels
  \node[above=0.3cm of I1] {\small Input};
  \node[above=0.3cm of H1] {\small Hidden};
  \node[above=0.3cm of O1] {\small Output};
\end{tikzpicture}
```

### Transformer Block

```latex
\begin{tikzpicture}[
  block/.style={rectangle, draw, rounded corners, minimum width=3cm,
    minimum height=0.8cm, fill=#1, font=\small},
  block/.default=gray!10,
  arr/.style={-{Stealth}, thick}
]
  \node[block=yellow!20] (attn) at (0,0) {Multi-Head Attention};
  \node[block=blue!10] (norm1) at (0,1.3) {Add \& LayerNorm};
  \node[block=green!20] (ffn) at (0,2.6) {Feed-Forward Network};
  \node[block=blue!10] (norm2) at (0,3.9) {Add \& LayerNorm};

  \draw[arr] (attn) -- (norm1);
  \draw[arr] (norm1) -- (ffn);
  \draw[arr] (ffn) -- (norm2);

  % Residual connections
  \draw[arr, dashed, gray] (attn.west) -- ++(-0.8,0) |- (norm1.west);
  \draw[arr, dashed, gray] (ffn.west) -- ++(-0.8,0) |- (norm2.west);
\end{tikzpicture}
```

## PGFPlots for Data Visualization

### Setup

```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
```

### Line Plot with Error Bars

```latex
\begin{tikzpicture}
\begin{axis}[
  width=0.8\textwidth,
  height=6cm,
  xlabel={Epoch},
  ylabel={Accuracy (\%)},
  legend pos=south east,
  grid=major,
  grid style={gray!30},
  tick label style={font=\small}
]
\addplot+[mark=o, thick, error bars/.cd, y dir=both, y explicit]
  coordinates {
    (1,72) +- (0,1.5)
    (5,85) +- (0,1.2)
    (10,91) +- (0,0.8)
    (20,94) +- (0,0.5)
    (50,96) +- (0,0.3)
  };
\addlegendentry{Our Method}

\addplot+[mark=square, thick, dashed]
  coordinates {(1,68) (5,79) (10,85) (20,89) (50,91)};
\addlegendentry{Baseline}
\end{axis}
\end{tikzpicture}
```

### Bar Chart Comparing Methods

```latex
\begin{tikzpicture}
\begin{axis}[
  ybar,
  width=10cm, height=6cm,
  symbolic x coords={BLEU, ROUGE-L, METEOR},
  xtick=data,
  ylabel={Score},
  ymin=0, ymax=100,
  bar width=12pt,
  legend style={at={(0.5,1.05)}, anchor=south, legend columns=3},
  nodes near coords,
  nodes near coords style={font=\tiny}
]
\addplot coordinates {(BLEU,45.2) (ROUGE-L,62.1) (METEOR,38.7)};
\addplot coordinates {(BLEU,52.8) (ROUGE-L,68.4) (METEOR,44.3)};
\addplot coordinates {(BLEU,58.1) (ROUGE-L,71.9) (METEOR,49.6)};
\legend{Baseline, +Pretraining, +Fine-tuning}
\end{axis}
\end{tikzpicture}
```

## Bayesian Network and Graphical Models

```latex
\begin{tikzpicture}[
  latent/.style={circle, draw, minimum size=1cm, fill=gray!20},
  observed/.style={circle, draw, minimum size=1cm, fill=white, thick},
  plate/.style={rectangle, draw, dashed, rounded corners, inner sep=10pt},
  arr/.style={-{Stealth}, thick}
]
  \node[latent] (theta) at (0,2) {$\theta$};
  \node[latent] (z) at (2,2) {$z_n$};
  \node[observed] (x) at (2,0) {$x_n$};
  \node[latent] (alpha) at (-1.5,2) {$\alpha$};

  \draw[arr] (alpha) -- (theta);
  \draw[arr] (theta) -- (z);
  \draw[arr] (z) -- (x);

  \node[plate, fit=(z)(x), label=below right:$N$] {};
\end{tikzpicture}
```

## Best Practices

- **Define styles globally.** Use `\tikzset{}` in the preamble so all figures share consistent colors and shapes.
- **Use relative positioning.** `right=2cm of nodeA` is more maintainable than absolute coordinates.
- **Externalize figures.** For large documents, use `\usetikzlibrary{external}` to cache compiled figures and speed up builds.
- **Match document fonts.** TikZ inherits the document font automatically -- this is a key advantage over external tools.
- **Export standalone figures.** Use the `standalone` document class to compile figures individually for reuse in presentations.
- **Keep source readable.** One node or drawing command per line, with comments explaining the visual structure.

## References

- [awesome-latex-drawing](https://github.com/xinychen/awesome-latex-drawing) -- 30+ LaTeX drawing examples (2,000+ stars)
- [TikZ and PGF Manual](https://tikz.dev/) -- Official documentation
- [PGFPlots Manual](https://pgfplots.net/) -- Data visualization in LaTeX
- [TikZ Examples](https://texample.net/tikz/examples/) -- Community gallery
- [LaTeX Drawing Tutorial](https://www.overleaf.com/learn/latex/TikZ_package) -- Overleaf tutorial

---

## Reusable Figure Collections

A skill providing ready-to-use LaTeX drawing examples and guidance for creating publication-quality scientific figures using TikZ, PGFPlots, and related packages. Based on awesome-latex-drawing (2K stars), this skill covers Bayesian networks, tensor decompositions, neural architectures, time series visualizations, and more.

## Overview

High-quality figures are essential for effective scientific communication. While external tools like Matplotlib or Inkscape can produce figures, native LaTeX drawings offer superior integration with the document, consistent typography, vector-quality output at any resolution, and automatic style matching with the surrounding text.

This skill equips the agent with knowledge of 30+ LaTeX drawing patterns commonly used in academic publications. Each pattern includes the required packages, a description of the drawing approach, and guidance on customization for specific research contexts.

## Essential Packages

The following LaTeX packages form the foundation for scientific drawing:

**TikZ (tikz)**
- The core drawing package for LaTeX, providing a programming interface for vector graphics
- Supports coordinate systems, transformations, path operations, and decorations
- Required for virtually all complex scientific diagrams
- Load with: `\usepackage{tikz}` and relevant libraries via `\usetikzlibrary{...}`

**PGFPlots (pgfplots)**
- Built on TikZ for creating publication-quality data plots
- Supports 2D and 3D plots, error bars, fill areas, and custom markers
- Handles axis formatting, legends, and annotations
- Load with: `\usepackage{pgfplots}` and `\pgfplotsset{compat=1.18}`

**TikZ Libraries**
- `arrows.meta` - customizable arrowhead styles
- `positioning` - relative node placement (above=of, right=of)
- `fit` - bounding boxes around groups of nodes
- `matrix` - grid-based node layouts
- `decorations.pathreplacing` - braces, zigzag, snake decorations
- `calc` - coordinate arithmetic
- `backgrounds` - layered drawing with background regions

## Bayesian Network Diagrams

Bayesian networks are among the most common diagrams in probabilistic modeling papers:

**Node Styles**
- Observed variables: filled circles or shaded nodes
- Latent variables: open (unfilled) circles
- Hyperparameters: small solid dots or fixed-value nodes
- Plates: rounded rectangles indicating repetition with index labels

**Construction Approach**
- Define node styles at the beginning of the tikzpicture environment
- Place nodes using relative positioning for maintainable layouts
- Draw directed edges with arrow styles indicating conditional dependencies
- Add plate notation around repeated variable groups
- Label edges with conditional probability annotations when needed

**Common Patterns**
- Latent Dirichlet Allocation (LDA) plate diagram
- Hidden Markov Model (HMM) chain structure
- Variational autoencoder (VAE) graphical model
- Gaussian mixture model (GMM) with plate notation
- Deep generative model hierarchies

## Tensor and Matrix Diagrams

For linear algebra and tensor decomposition papers:

**Tensor Representations**
- Matrices as 2D grids with element shading
- Third-order tensors as 3D cubes with visible faces
- Tensor networks as connected node diagrams
- Factor matrices as thin rectangular blocks

**Decomposition Visualizations**
- CP decomposition: tensor equals sum of rank-one components
- Tucker decomposition: core tensor multiplied by factor matrices
- Tensor train: chain of connected 3D cores
- Matrix factorization: large matrix as product of thin matrices

## Neural Network Architectures

For deep learning and machine learning papers:

**Layer Representations**
- Fully connected layers as columns of nodes with all-to-all connections
- Convolutional layers as stacked feature map grids
- Attention layers as matrix operation diagrams
- Recurrent connections as self-loops or unrolled sequences

**Architecture Patterns**
- Encoder-decoder structures with bottleneck
- Skip connections and residual blocks
- Multi-head attention mechanisms
- Transformer block diagrams

## Time Series and Spatiotemporal Plots

For data analysis and forecasting papers:

**Time Series Elements**
- Line plots with confidence bands using PGFPlots fill between
- Missing data indicators with dashed segments
- Multi-variate time series as stacked or aligned panels
- Seasonal decomposition as vertically arranged subplots

**Spatiotemporal Grids**
- Heatmaps using TikZ matrix with color-coded cells
- Geographic grids with observation points
- Temporal slices showing spatial evolution

## Customization Guidelines

When adapting templates for specific publications:

- Match the font size to the document class (typically 8-10pt for figure labels)
- Use consistent color schemes that work in both color and grayscale
- Align arrow styles across all figures in the paper
- Keep node sizes proportional to their importance in the diagram
- Add descriptive labels rather than relying solely on mathematical notation
- Test figures at the target column width before finalizing

## Integration with Research-Claw

This skill supports the Research-Claw writing workflow:

- Generate LaTeX drawing code from verbal descriptions of desired figures
- Adapt existing templates to match specific research contexts
- Debug TikZ compilation errors and suggest fixes
- Recommend appropriate diagram types for different data structures
- Produce standalone compilable .tex files for figure testing

## Best Practices

- Always use relative positioning instead of absolute coordinates for maintainability
- Define reusable styles at the document or figure level to ensure consistency
- Compile figures as standalone documents first, then include in the main paper
- Use `\footnotesize` or `\scriptsize` for labels inside dense diagrams
- Export to PDF for vector quality and include via `\includegraphics`
- Keep TikZ code well-commented for future modifications by collaborators

---

## TikZ Quick Reference

A skill for creating publication-quality scientific diagrams directly in LaTeX using the TikZ package. Covers basic drawing commands, flowcharts, neural network architectures, data flow diagrams, and integration with PGFplots for camera-ready figures.

## Getting Started with TikZ

### Basic Setup

```latex
\documentclass{article}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning, shapes.geometric, calc, fit}

\begin{document}
\begin{tikzpicture}
  % Your drawing commands here
\end{tikzpicture}
\end{document}
```

### Fundamental Drawing Commands

```latex
% Lines and shapes
\draw (0,0) -- (3,0) -- (3,2) -- cycle;          % Triangle
\draw[thick, ->] (0,0) -- (4,0);                  % Arrow
\draw[dashed, blue] (0,0) circle (1.5);            % Dashed circle
\filldraw[fill=gray!20, draw=black] (2,1) ellipse (1 and 0.5);

% Nodes (text labels with optional shapes)
\node[draw, rectangle, minimum width=2cm] (A) at (0,0) {Input};
\node[draw, circle] (B) at (3,0) {Process};
\draw[->] (A) -- (B);

% Relative positioning (requires positioning library)
\node[draw, rectangle] (C) [right=2cm of B] {Output};
\draw[->] (B) -- (C);
```

## Common Scientific Diagrams

### Flowcharts

```latex
\begin{tikzpicture}[
    block/.style={rectangle, draw, fill=blue!10, text width=5em,
                  text centered, rounded corners, minimum height=3em},
    decision/.style={diamond, draw, fill=green!10, text width=4em,
                     text centered, inner sep=0pt, aspect=2},
    line/.style={draw, -Stealth}
]
  \node[block] (data) {Collect Data};
  \node[block, below=1cm of data] (clean) {Clean \& Preprocess};
  \node[decision, below=1cm of clean] (valid) {Valid?};
  \node[block, below=1cm of valid] (analyze) {Analyze};
  \node[block, right=2cm of valid] (fix) {Fix Issues};

  \path[line] (data) -- (clean);
  \path[line] (clean) -- (valid);
  \path[line] (valid) -- node[right] {Yes} (analyze);
  \path[line] (valid) -- node[above] {No} (fix);
  \path[line] (fix) |- (clean);
\end{tikzpicture}
```

### Neural Network Architecture

```latex
\begin{tikzpicture}[
    neuron/.style={circle, draw, minimum size=0.8cm, fill=orange!20},
    layer/.style={rectangle, draw, dashed, inner sep=0.3cm}
]
  % Input layer
  \foreach \i in {1,2,3,4} {
    \node[neuron] (I\i) at (0, -\i*1.2) {};
  }

  % Hidden layer
  \foreach \j in {1,2,3} {
    \node[neuron, fill=blue!20] (H\j) at (3, -\j*1.2 - 0.6) {};
  }

  % Output layer
  \foreach \k in {1,2} {
    \node[neuron, fill=green!20] (O\k) at (6, -\k*1.2 - 1.2) {};
  }

  % Connections
  \foreach \i in {1,2,3,4} {
    \foreach \j in {1,2,3} {
      \draw[->] (I\i) -- (H\j);
    }
  }
  \foreach \j in {1,2,3} {
    \foreach \k in {1,2} {
      \draw[->] (H\j) -- (O\k);
    }
  }

  % Labels
  \node[above=0.5cm of I1] {Input};
  \node[above=0.5cm of H1] {Hidden};
  \node[above=0.5cm of O1] {Output};
\end{tikzpicture}
```

## Integration with PGFplots

### Combining Diagrams and Plots

```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}

\begin{tikzpicture}
\begin{axis}[
    xlabel={Epoch},
    ylabel={Loss},
    legend pos=north east,
    grid=major,
    width=8cm, height=6cm
]
  \addplot[blue, thick, mark=none] table {
    1  0.95
    5  0.72
    10 0.45
    20 0.22
    30 0.15
    50 0.08
  };
  \addlegendentry{Training}

  \addplot[red, thick, dashed, mark=none] table {
    1  0.98
    5  0.75
    10 0.52
    20 0.35
    30 0.30
    50 0.28
  };
  \addlegendentry{Validation}
\end{axis}
\end{tikzpicture}
```

## Tips for Publication-Quality Figures

### Style Guidelines

```
1. Font consistency:
   - Use the same font family as your document body
   - Minimum 8pt for axis labels and annotations
   - Match font size to caption text

2. Color considerations:
   - Use colorblind-friendly palettes (avoid red-green only)
   - Ensure figures are readable in grayscale
   - Use patterns or line styles as secondary differentiators

3. Size and resolution:
   - TikZ produces vector output (PDF) -- always sharp
   - Set figure width to match column width (single or double)
   - Use consistent sizing across all figures in the paper

4. Labeling:
   - Label all axes with units
   - Use (a), (b), (c) for sub-figures
   - Place legends inside the plot area when possible
```

### Exporting Standalone TikZ Figures

```latex
% standalone.tex -- compile separately, include as PDF
\documentclass[tikz, border=2mm]{standalone}
\usetikzlibrary{arrows.meta, positioning}
\begin{document}
\begin{tikzpicture}
  % ... your diagram ...
\end{tikzpicture}
\end{document}

% In your main document:
% \includegraphics{standalone.pdf}
```

## Useful TikZ Libraries

| Library | Purpose |
|---------|---------|
| `positioning` | Relative node placement (right=of, below=of) |
| `arrows.meta` | Modern arrow tip styles |
| `shapes.geometric` | Diamond, trapezium, ellipse nodes |
| `calc` | Coordinate calculations |
| `fit` | Fit a node around a set of other nodes |
| `decorations.pathreplacing` | Braces, snakes, zigzag lines |
| `backgrounds` | Draw behind other elements |
| `matrix` | Grid-based node layouts |
