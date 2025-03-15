
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

## data.cs
- [ ] Declare data class for base cells.
  - [ ] Declare get & set functions for each attribute.
- [ ] Declare child data class for zoned cells from base cells.
  - [ ] Declare get & set functions for each attribute.
- [ ] Declare a class that acts as a hash for cell-level updates between time steps (may handle this differently).
  - [ ] Declare get & set functions for each attribute.
- [ ] Function to create a 2D array template of multiple types (char, cell, hash).

## io.cs
- [ ] Input Function - Open and read contents of file.
  - [ ] Validate the file exists.
- [ ] IO Function - Print out a message to the user, and take a file name as input.
  - [ ] Take region layout file name from the input filename and validate it exists.
- [ ] Output Function - Print out basic information for each time step.
- [ ] Output Function - Print out region layout state (incorporate spacing based on values).
- [ ] Output Function - Print out regional analysis information.

## zone-residential.cs
- [ ] Growth Function
  - [ ] Take an R zoned cell (validate that it is R type if passing logic does not).
  - [ ] Get the cell's population & adjacent cell X & Y coordinates.
  - [ ] If the cell's population is 0...
    - [ ] ...and is next to a T or # or its neighboring population is 1+, increment the cell's population.
  - [ ] If the cell's population is 1, 2, or 3...
    - [ ] ...and its neighboring population is its population x2 or greater, increment the cell's population.
  - [ ] If the cell's population is 4 or greater...
    - [ ] ...and its neighboring population is 8 or greater, increment the cell's population.
  - [ ] If the cell's population is increased, increase the number of available workers by the same amount.

## zone-industrial.cs
- [ ] Growth Function
  - [ ] Verify there is at least 2 workers available & break the growth function if not.
  - [ ] Take an I zoned cell (validate that it is I type if passing logic does not).
  - [ ] 

## zone-commercial.cs

## pollution.cs
- [ ] Pollution Calculation - Take the final region state layout, and distribute pollution accordingly.
  - I cell pollution is equal to its population.
  - Pollution in other cells is equal to the nearest I cell pollution minus the shortest distance of X & Y values.

## analysis.cs
- [ ] Function to update the number of available workers by the amount passed to it.
  - Pass positive numbers for addition and negative for subtraction.
- [ ] Function to update the number of available goods by the amount passed to it.
  - Pass positive numbers for addition and negative for subtraction.


## BRAINSTORMING
- Tracking growth - is there a need to track the whole grid?
  - I could only track the zoned cells that grow and ignore the rest.
    - If I store them as a list of zoned cells, I could sort them based on prioritization criteria
    - Then I process their growth in order.
- Prioritization rules - I need to make sure not to forget about these since they are vital to growth choices.

