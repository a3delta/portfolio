
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
- **Region Layout**
  - \[*array*\]\[*array*\]\[*char*\] cell layout
    - Regional layout of cell types as a flat rectangle from a matrix in CSV format.
- **Base Cell Class**
  - \[*char*\] type
    - Cell types can be represented as a single letter (may update to string when adding features).
  - \[*int*\] pollution
    - All cells can acquire pollution levels.
- **Zoned Cell Class**
  - \[*int*\] population
    - All zoned cells have a population.
  - \[*array*\]\[*tuple*\] adjacencies
    - All zoned cells have rules regarding adjacenices comparisons.
    - Storing will be faster than calculating (if space becomes an issue, switch to calculated adjacencies).
  - \[*int*\] workers
    - For residential cells, this tracks the count of the population that works (residential population provides workers at a 1:1 ratio).
    - For industrial & commercial cells, this tracks the number of workers assigned to the cell.
- **Industry/(Industrial & Commercial) Cell Class**
  - \[*int*\] goods
    - For industrial cells, this tracks the count of sold goods (industrial population provides goods at a 1:1 ratio).
    - For commercial cells, this tracks the number of goods assigned to the cell.
- **Cell Matrix**
  - \[*array*\]\[*array*\]\[*cell*\] cells with full data based on inheritance
    - Cells can be accessed fast due to their ordered congruous layout.
    - Searching, insertions, and deletions are not necessary for this simulation (if they were, this type should be re-evaluated).
    - Choosing this over multiple simple 2D arrays/matrices since multiple matrices would result in unnecessary additional space usage.
- **Next Time Step Matrix**
  - \[*array*\]\[*array*\]\[*hash*\] changes to make to the region on the next time step
    - Hash tables should have 3 keys for population, workers, and goods containing ints of how much to change those values by.

## main.cs
- [ ] Input - Prompt user for a configuration file name.
  - [ ] Validate Configuration - Verify the file is valid. Reprompt if not valid.
  - [ ] Read Configuration - Read in configuration data.
  - [ ] Validate Region Layout - Verify the region layout file is valid. Exit if not valid.
  - [ ] Read Region Layout - Read in the region layout.
- [ ] Initialize Region Data
  - [ ] Build - Construct the region data based on the region layout.
  - [ ] Set X & Y Max - Initialize the max X & Y coordinates.
  - [ ] Set Time Limit - Initialize the time limit based on the configuration data.
  - [ ] Set Refresh Rate - Initialize the refresh rate based on the configuration data.
- [ ] Initialize Next Time Step Matrix
- [ ] Output - Print the initial region state.
- [ ] Loop
  - [ ] Cell Updates v1 (copies what was done in the original C++ version, not sure if it scales accurately)
    - [ ] Run updates on all commercial cells.
    - [ ] Run updates on all industrial cells.
    - [ ] Run updates on all residential cells.
  - [ ] Cell Updates v2
    - [ ] Iterate through each cell down the X axis for each point on the Y axis.
      - [ ] Run updates on the cell based on what it is zoned as (this may run into prioritization issues).
  - [ ] Run updates on pollution.
  - [ ] Output - Print the current time step, available workers, and available goods.
  - [ ] Determine if the current time step is divisible by the refresh rate.
    - [ ] If so, print the current region state.
  - [ ] Determine if there are any changes between the current time step and the next.
    - [ ] If not, end the simulation.
- [ ] Output - Print the final region state.
- [ ] Output - Print the final pollution state.
- [ ] Output - Print the full regional analysis.
- [ ] Input - Prompt for a selective regional analysis using min & max X & Y limits.
  - [ ] Validate X & Y Limits - Verify they are within in range. Prompt for new limits if not.
- [ ] Output - Print the selective regional analysis.
- [ ] End the simulation.

## data.cs

## io.cs

## zone-residential.cs

## zone-industrial.cs

## zone-commercial.cs

## pollution.cs

## analysis.cs

