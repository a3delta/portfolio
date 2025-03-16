
# PLANNING

## About
This document is used for planning how to approach the design of this project, from data structures to functional breakdowns and how files are laid out.

## Files
- [ ] Program.cs - This will be the core code where all function calls are made.
- [ ] Data.cs - This will be where data structures and their functions are defined.
- [ ] IO.cs - This will be where data input and output functions are defined.
- [ ] Zone-Residential.cs - This will be where residential zone functions are defined.
- [ ] Zone-Industrial.cs - This will be where industrial zone functions are defined.
- [ ] Zone-Commercial.cs - This will be where commercial zone functions are defined.
- [ ] Pollution.cs - This will be where pollution functions are defined.
- [ ] Analysis.cs - This will be where whole & partial regional analysis functions are defined.

## Data Types
- **Region Layout**
  - \[*array*\]\[*array*\]\[*char*\] cell layout
    - Regional layout of cell types as a flat rectangle from a matrix in CSV format.
    - Used when checking adjacency information & printing region states.
- **Zoned Cell Class**
  - \[*char*\] type
    - Cell types can be represented as a single letter (may update to string when adding features).
  - \[*int*\] population
    - All zoned cells have a population.
  - \[*array*\]\[*tuple*\] adjacencies
    - All zoned cells have rules regarding adjacenices comparisons.
    - Calculated once at initialization.
    - Storing will be faster than calculating (if space becomes an issue, switch to calculated adjacencies).
  - \[*int*\] adjacent population
    - Used for growth prioritization.
  - \[*int*\] next population update
    - This will hold the population update for this cell during the next time step.
- **Zoned Cell Hash Table**
  - \[*hash*\]\[*cell*\] table of zoned cells
    - Hash table keys will be strings of X/Y coordinate tuples.
    - Zoned cells are the only cells that will be altered by growth in this simulation.
    - Cell data can be retrieved fast due to the fast lookup capabilities of hash tables.
    - This data structure will not be sorted, inserted into, or deleted from after initialization.
- **Growth Priority Array**
  - \[*array*\]\[*string*\] ordered cell coordinate tuples
    - Cell coordinate tuples will be ordered based on growth prioritization rules.
    - An array is easy and fast to iterate through, and insertions have a comparable time complexity to linked lists.
- **Analysis Variables**
  - \[*int*\] workers (available)
    - NOT NEEDED: workers total *This is the total R population; no need to track this outside of regional analysis.*
    - NOT NEEDED: workers unavailable *By tracking the R population well enough, this will not be necessary.*
    - NOTE: Only increase with R population increases (which only happen in increments) to avoid bad counts.
    - NOTE: Since R population can only work 1 job each, no additional tracking is necessary.
  - \[*int*\] goods (available)
    - NOT NEEDED: goods total *This is the total I population; no need to track this outside of regional analysis.*
    - NOT NEEDED: goods unavailable *By tracking the I population well enough, this will not be necessary.*
    - NOTE: Only increase with I population increases (which only happen in increments) to avoid bad counts.
    - NOTE: Since I population can only provide 1 good each, no additional tracking is necessary.
  - \[*array*\]\[*array*\]\[*int*\] pollution matrix
    - All cells can acquire pollution.
    - Pollution is only reported at the end, so calculation is only necessary then.

## Program.cs
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
  - [ ] Cell Updates
    - [ ] Order zoned cells based on growth priority rules.
    - [ ] Iterate through each zoned cell.
      - [ ] If an R cell, run residential growth updates.
      - [ ] If a C cell, run commercial growth updates.
      - [ ] If an I cell, run industrial growth updates.
    - [ ] Update adjacenct cell populations for each zoned cell.
  - [ ] Output - Print the current time step, available workers, and available goods.
  - [ ] Determine if the current time step is divisible by the refresh rate.
    - [ ] If so, print the current region state.
  - [ ] Determine if there are any changes between the current time step and the next.
    - [ ] If not, end the simulation.
- [ ] Output - Print the final region state.
- [ ] Output - Calculate & print the final pollution state.
- [ ] Output - Print the full regional analysis.
- [ ] Input - Prompt for a selective regional analysis using min & max X & Y limits.
  - [ ] Validate X & Y Limits - Verify they are within in range. Prompt for new limits if not.
- [ ] Output - Print the selective regional analysis.
- [ ] End the simulation.

## Data.cs
- [ ] Function to create a 2D array template of multiple types (char, int).
  - *char* is used for the base region layout.
  - *int* is used for the pollution analysis layout.
- [ ] Declare data class for zoned cells from base cells.
  - [ ] Declare get & set functions for each attribute.

## IO.cs
- [ ] Input Function - Open and read contents of file.
  - [ ] Validate the file exists.
- [ ] IO Function - Print out a message to the user, and take a file name as input.
  - [ ] Take region layout file name from the input filename and validate it exists.
- [ ] Output Function - Print out basic information for each time step.
- [ ] Output Function - Print out region layout state (incorporate spacing based on values).
- [ ] Output Function - Print out regional analysis information.

## Zone-Residential.cs
- [ ] Growth Function of R zoned cells
  - [ ] Update cell's population by the amount specified in the next population update attribute.
  - [ ] Reinitialize the cell's next population update attribute to 0.
  - [ ] If the cell's population is 0...
    - [ ] ...and is next to a T or # or its adjacent to 1+ cells with a population of 1+, increment the cell's next population update.
  - [ ] If the cell's population is 1, 2, or 3...
    - [ ] ...and its adjacent to 2+, 4+, or 6+ cells with a population of 1+, 2+, or 3+, increment the cell's next population update.
  - [ ] If the cell's population is 4+...
    - [ ] ...and its adjacent to 8+ cells with a population of 4+, increment the cell's next population update.
  - [ ] If the cell's population is increased, increase the number of available workers by the same amount.

## Zone-Industrial.cs
- [ ] Growth Function of I zoned cells
  - [ ] Update cell's population by the amount specified in the next population update attribute.
  - [ ] Reinitialize the cell's next population update attribute to 0.
  - [ ] Verify there is at least 2 workers available & break the growth function if not.
  - [ ] If the cell's population is 0...
    - [ ] ...and is next to a T or # or its adjacent to 1+ cells with a population of 1+, increment the cell's next population update.
  - [ ] If the cell's population is 1...
    - [ ] ...and its adjacent to 2+ cells with a population of 1+, increment the cell's next population update.
  - [ ] If the cell's population is 2+...
    - [ ] ...and its adjacent to 4+ cells with a population of 2+, increment the cell's next population update.
  - [ ] If the cell's population is increased, increase the number of available goods by the same amount.
  - [ ] If the cell's population is increased, decrease the number of available workers by 2.

## Zone-Commercial.cs
- [ ] Growth Function of C zoned cells
  - [ ] Update cell's population by the amount specified in the next population update attribute.
  - [ ] Reinitialize the cell's next population update attribute to 0.
  - [ ] Verify there is at least 1 worker & 1 good available & break the growth function if not.
  - [ ] If the cell's population is 0...
    - [ ] ...and is next to a T or # or its adjacent to 1+ cells with a population of 1+, increment the cell's next population update.
  - [ ] If the cell's population is 1...
    - [ ] ...and its adjacent to 2+ cells with a population of 1+, increment the cell's next population update.
  - [ ] If the cell's population is increased, decrease the number of available workers & goods by 1 each.

## Pollution.cs
- [ ] Pollution Calculation - Take the final region state layout, and distribute pollution accordingly.
  - I cell pollution is equal to its population.
  - Pollution in other cells is equal to the nearest I cell pollution minus the shortest distance of X & Y values.

## Analysis.cs
- [ ] Function to update the number of available workers by the amount passed to it.
  - Pass positive numbers for addition and negative for subtraction.
- [ ] Function to update the number of available goods by the amount passed to it.
  - Pass positive numbers for addition and negative for subtraction.
- [ ] Function to build out the ordered zoned cell array for growth simulation.
  - [ ] 1. C cells are prioritized over I cells.
  - [ ] 2. Between 2 cells, the cell with a larger population is prioritized.
  - [ ] 3. Between 2 cells, the cell with a larger total adjacent population is prioritized.
  - [ ] 4. Between 2 cells, the cell with the smaller Y coordinate is prioritized.
  - [ ] 5. Between 2 cells, the cell with the smaller X coordinate is prioritized.


## BRAINSTORMING
- Adjacencies - What about consideration for the number of cells with populations?
  - Is that necessary, or do all updates happen solely with a high enough adjacent population?
  - For instance, if there are 2+ adjacent cells with a population of 2+....
    - ...does this mean that it doesn't update if there is only 1 adjacent cell, even if it has a population of 2+?
    - ...or could this mean that it doesn't update if there are 2 adjacent cells, but they have a population of 1 & 3?
  - ANSWER: Each of the x+ adjacent cells must have a population of y+.
- Do I need a function to update adjacent population values?
  - ANSWER: No, because this will be covered by set methods in the class definition.

