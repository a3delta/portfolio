
# READ ME

## Intent
To rework my existing `sim-city` project in `c#` to practice `c#` and rework the project into something better and 100% done by me.

## Note
This was a college project, so the instructions provided will be listed out as the base project. As I come up with new ideas for additional features, I will add them to extend the project. Any additonal features will only be added after the base project is completed.

## About
The intent of this project is to simulate the growth of a city over time with a focus on residential, commercial, and industrial zones and how pollution affects the overall development.

## Base Project - Wiki

**High-Level Design**
- [ ] One page covering the high-level design of the entire system.
- [ ] Must contain a UML diagram of the entire system.
- [ ] Describe each major component of the system.
  - [ ] Link each description to its respective wiki page.
  - [ ] Briefly describe the component.
  - [ ] Briefly describe how each component works together.
- [ ] Briefly describe each major data structure used across the project.

**Major Component Design**
- One page covering the design of each major component in the system.
  - Section 1/3: Briefly describe of the purpose of the component.
  - Section 2/3: Describe how the data was stored & maintained.
    - What objects were created for storage?
    - How are the organized & managed?
    - What formal data structures (graphs, trees, arrays, hashes, etc.) are used?
  - Section 3/3: Describe the component's functionality.
    - What are the major functions of the component?
    - How do the major functions work?
    - How is the data moved & transformed?
    - How is the data read & output?
  - Bonus: Include UML diagrams to describe how the component works.
- [ ] Component 1: Reading in input files & initializing the simuation.
  - [ ] Section 1/3
  - [ ] Section 2/3
  - [ ] Section 3/3
  - [ ] Bonus
- [ ] Component 2: R zone functions (data storage, rules, & transformations).
  - [ ] Section 1/3
  - [ ] Section 2/3
  - [ ] Section 3/3
  - [ ] Bonus
- [ ] Component 3: C zone functions (data storage, rules, & transformations).
  - [ ] Section 1/3
  - [ ] Section 2/3
  - [ ] Section 3/3
  - [ ] Bonus
- [ ] Component 4: I zone functions (data storage, rules, & transformations).
  - [ ] Section 1/3
  - [ ] Section 2/3
  - [ ] Section 3/3
  - [ ] Bonus
- [ ] Component 5: Pollution functions (data storage, rules, & transformations).
  - [ ] Section 1/3
  - [ ] Section 2/3
  - [ ] Section 3/3
  - [ ] Bonus
- [ ] Component 6: Analysis of the region & desired area (outputs & totals).
  - [ ] Section 1/3
  - [ ] Section 2/3
  - [ ] Section 3/3
  - [ ] Bonus

## Base Project - Implementation

**Notes**
- The region is a flat plane, so no edges wrap around to connect to another.
- Cells are adjacent if they share edges or corners (for a max of 8 and a min of 3 other cells).
- Each zoned cell will change their state according to simulation rules.

**Data**
- [ ] Read & store the simulation configuration data from the user.
  - [ ] Must take any file name (no prompting for file name).
  - 1st line: Provides the name of the file containing the region layout.
  - 2nd line: Provides the maximum number of time steps the simulation will run.
  - 3rd line: Provides the refresh rate for how often the current state of the region is output to the user during the simulation.
- [ ] Read & store the initial region layout.
  - The file will be in CSV format.
  - The region will be any size of rectangle.
  - The region contains 0 pollution at the start of simulation.
  - R: Residential zone.
  - I: Industrial zone.
  - C: Commercial zone.
  - -: Road.
  - T: Powerline.
  - \#: Powerline over a road.
  - P: Power plant.

**Simulation - General**
- [ ] The simulation should halt when...
  - [ ] There is no change between 2 consecutive time steps.
  - [ ] The time limit has been reached.
- [ ] Output the initial region state as time step 0.
  - [ ] If a cell is zoned as R, I, or C & has a population of 0, display the letter identifying the zoning for the cell instead of the population.
- [ ] Output the final region state.
- [ ] Output the total regional population for R, I, & C zones.
- [ ] Output the final regional pollution state.
- [ ] Output the total pollution in the region.
- [ ] Prompt the user for coordinates of some rectangular are of the region.
  - [ ] Perform bounds check to make sure the coordinates are in bounds.
  - [ ] Reprompt user for coordinates if previous were out of bounds.
  - [ ] Output the total population for R, I, & C zones within the specified area.
  - [ ] Output the total pollution within the area specified.
- [ ] At each time step, except time step 0...
  - [ ] Output the current time step.
  - [ ] Output the number of available workers.
  - [ ] Output the number of available goods.
- [ ] The region state should be output at intervals denoted by the refresh rate.
- [ ] Apply the following rules in order when deciding how growth is applied:
  - [ ] 1. C cells are prioritized over I cells.
  - [ ] 2. Between 2 cells, the cell with a larger population is prioritized.
  - [ ] 3. Between 2 cells, the cell with a larger total adjacent population is prioritized.
  - [ ] 4. Between 2 cells, the cell with the smaller Y coordinate is prioritized.
  - [ ] 5. Between 2 cells, the cell with the smaller X coordinate is prioritized.
- [ ] The top left cell has the [X,Y] coordinates of [0,0].
- [ ] All rules are evaluated at the current time step & all values are updated during the next time step.
- [ ] R population provides workers to I & C zones, but each worker can only have one job.
- [ ] I population provides goods to the C zones at a rate of 1 good / population, but each good can only be sold at 1 C cell.
- [ ] I cells produce pollution = its population, and polution spreads to all adjacent cells at a rate of one less unit of pollution per cell away from the source.

**Simulation - Residential**
- [ ] For the following conditions, increment an R cell's population:
  - [ ] If its population = 0 & is adjacent to a T or #.
  - [ ] If its population = 0 & is adjacent to 1+ cells with a population of 1+.
  - [ ] If its population = 1 & is adjacent to 2+ cells with a population of 1+.
  - [ ] If its population = 2 & is adjacent to 4+ cells with a population of 2+.
  - [ ] If its population = 3 & is adjacent to 6+ cells with a population of 3+.
  - [ ] If its population = 4 & is adjacent to 8+ cells with a population of 4+.

**Simulation - Industrial**
- [ ] For the following conditions, increment an I cell's population & assign the available workers to that job if there are 2+ available workers:
  - [ ] If its population = 0 & it is adjacent to a T or #.
  - [ ] If its population = 0 & it is adjacent to 1+ cells with a population of 1+.
  - [ ] If its population = 1 & it is adjacent to 2+ cells with a population of 1+.
  - [ ] If its population = 2 & it is adjacent to 4+ cells with a population of 2+.

**Simulation - Commercial**
- [ ] For the following conditions, increment a C cell's population and assign 1 available worker & 1 good to that job if there are 1+ workers & 1+ goods available:
  - [ ] If its population = 0 & it is adjacent to a T or #.
  - [ ] If its population = 0 & it is adjacent to 1+ cells with a population of 1+.
  - [ ] If its population = 1 & it is adjacent to 2+ cells with a population of 1+.

## Additional Functionality - Stretch Goals
- [ ] Create a script/program that will randomly generate base input files for the main program.
- [ ] Optimize the logic where possible to reduce time and space usage.
- [ ] Incorporate parallelization/multithreading where possible.
- [ ] Update to incorporate elevation differences across a region (like a region with varying terrain).
- [ ] Update to incorporate elevation overlaps across a region (like a region with levels and terrain such as a building or cities with levels).
- [ ] Update to incorporate region wrapping (like a region that is formed in a band around a globe or the surface of a globe).
- [ ] Update to incorporate incongruous region layouts, such as islands or large gaps between zones (reducing the minimum number of adjacent cells down to 0).
- [ ] Update to incorporate unzoned cells with logic on how they will become zoned unless deemed unzonable.
- [ ] Update to incorporate other zoning types, such as nature preserve or historically significant, and rules to apply to each.
- [ ] Update to incorporate natural events such as weather or animal influence.
- [ ] Update to incorporate human events.
- [ ] Integrate with other simulation projects, like contagion.

