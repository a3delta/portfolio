
# PLANNING

## About
This document is used for planning how to approach the design of this project, from data structures to functional breakdowns and how files are laid out.

## Files
- [ ] main.cs - This will be the core code where all function calls are made.
- [ ] data.cs - This will be where data structures and their functions are defined.
- [ ] io.cs - This will be where data input and output functions are defined.
- [ ] zone-residential.cs - This will be where residential zone functions are defined.
- [ ] zone-industrial.cs - This will be where industrial zone functions are defined.
- [ ] zone-commercial.cs - This will be where commercial zone functions are defined.
- [ ] pollution.cs - This will be where pollution functions are defined.
- [ ] analysis.cs - This will be where whole & partial regional analysis functions are defined.

## Data Types
- **Region Layout** - *2D array* since it is a flat rectangle as a matrix in CSV format.
- **Base Cell Class**
  - *char* for cell type, since cell types can be represented as a single letter (may update to string).
  - *int* for cell pollution, since all cells can acquire pollution levels.
- **Zoned Cell Class**
  - population
  - adjacencies
- **Industrial Cell Class**
  - workers
- **Commercial Cell Class**
  - workers
  - goods
- **Cell Matrix** - *2D array of class objects* since cells can be accessed fast due to their ordered congruous layout.
  - Searching, insertions, and deletions are not necessary for this simulation (if they were, this type should be re-evaluated).
- Ideas
  - Represent the region as a matrix of cells stored in 2D arrays?
  - Represent each attribute as its own 2D array/matrix (a 2D array of the region layout, another of the pollution, population, workers, etc)?

## main.cs

## data.cs

## io.cs

## zone-residential.cs

## zone-industrial.cs

## zone-commercial.cs

## pollution.cs

## analysis.cs

