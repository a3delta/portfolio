
# DESIGN

**Intent:**
To rework my existing `sim-city` project in `c#` to practice `c#` and rework the project into something better and 100% done by me.

**Note:**
This was a college project, so the instructions provided will be listed out as the base project. As I come up with new ideas for additional features, I will add them to extend the project. Any additonal features will only be added after the base project is completed.

**About:**
The intent of this project is to simulate the growth of a city over time with a focus on residential, commercial, and industrial zones and how pollution affects the overall development.

**Base Project - Wiki:**
- [] One page covering the high-level design of the entire system.
  - [] Provide a brief description of each major functionality component.
  - [] Provide a brief description of how each major functionality component works together.
  - [] Provide a brief description of each of the major data structures used across the project.
  - [] Must contain a UML diagram of the entire system.
  - [] Must contain links to all of the major functionality component wiki pages.
- [] One page each covering the design of each major functionality component in the system.
  - [] Section 1/3: A brief description of the purpose of the component.
  - [] Section 2/3: A description of how the data was stored and maintained for this component.
    - What objects were created for storage, how are the organized & managed, and what formal data structures (graphs, trees, arrays, hashes, etc) are used?
  - [] Section 3/3: A description of the component's functionality.
    - What are the major functions of the component, how do they work, how is the data moved & transformed, and how is it read & output?
  - [] Bonus: Include UML diagrams to describe how the component works.

**Base Project - Implementation:**
- [] Read & store the simulation configuration data from the user.
  - [] Must take any file name (no prompting for file name).
  - First line: Will provide the name of the file containing the region layout.
  - Second line: Will provide the maximum number of time steps the simulation can take.
  - Third line: Will provide the refresh rate for how often the current state of the region is output to the user during the simulation.
- [] Read & store the initial region layout.
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
- [] Output the initial region state.
  - [] If a cell is zoned as R, I, or C and has a population of 0, display the letter identifying the zoning for the cell instead of the population.
  - The initial region state can be interpretted as time step 0.
- [] 

**Additional Functionality:**
- [] Create a script/program that will randomly generate base input files for the main program.

