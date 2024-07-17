#ifndef ZONEFUNCS_H
#define ZONEFUNCS_H

//INCLUDES
#include <fstream>
#include <string>
#include <iostream>
#include "dataMan.h"

//COMMERCIAL ZONE FUNCTION PROTOTYPES
class Commercial {
    public:
		//Contructor - no destructor since nothing is dynamic
        Commercial();
		
		//logical functions - check for growth potential, values that can change are pass by reference
		void growCommercial(Region &reg);

};

//INDUSTRIAL ZONE FUNCTION PROTOTYPES
class Industrial {
	public:		
		Industrial();			// Industrial constructor
		void IPopCheck(Region &reg);	// Evaluates conditions to adding population
};

//RESIDENTIAL ZONE FUNCTION PROTOTYPES
class Resident
{
	public://CONSTRUCTOR AND FUNCTIONS
	
		//Constructor: Takes in Cell Data to Initialize values
		Resident();

		void ResCheck(Region &r);//Needs the region for adjacency checks
		//It will loop through the array of cells until it fine cell.zone "R",it will check the current cell population to check if the population increases b/c of powerlines or adjacent

};

#endif
