#include "zoneFuncs.h"

//COMMERCIAL ZONE FUNCTION DEFINITIONS
//constructer
Commercial::Commercial(){}

//logical functions - check for growth potential, values that can change are pass by reference
void Commercial::growCommercial(Region &reg){
	int e;		//To store the value of getListItem()

	//PRIORITIZE RESIDENTIAL CELLS FOR POPULATION INCREASE
	reg.prioritizeCells('C');

	//loop through whole region
	for (int i = 0; i < reg.cellListSize(); i++){

		//SET ELEMENT
		e = reg.getListItem(i);

		//check if at least 1 worker and 1 good are available
		if ( (reg.getWorkers() >= 1) && (reg.getGoods() >= 1) ){
			if( (reg.cellPop(e) == 0) && (reg.byPower(e) == true) ){
				//increase population
				reg.incCellPop(e);
			}
			else if (reg.cellPop(e) == 0 && reg.adjPop(1, e) > 0){
				//increase population
				reg.incCellPop(e);
			}
			else if (reg.cellPop(e) == 1 && reg.adjPop(1, e) > 1){
				//increase population
				reg.incCellPop(e);
			}
		}
	}
	
	return;
}

//INDUSTRIAL ZONE FUNCTION DEFINITIONS
Industrial::Industrial() {
	// Default constructor
}

// FOR CHECKING & MODIFYING INDUSTRIAL POPULATION
void Industrial::IPopCheck(Region &reg) {
	int e;		//To store the value of getListItem()

	//PRIORITIZE RESIDENTIAL CELLS FOR POPULATION INCREASE
	reg.prioritizeCells('I');

	for (int i = 0; i < reg.cellListSize(); i++) {
		//SET ELEMENT
		e = reg.getListItem(i);

		//if the number of available workers is >= 2, check cell population
		if(reg.getWorkers() >= 2){
			// If zone has population of 0 - two checks within
			if (reg.cellPop(e) == 0) {
				// If zone is by powerline
				if (reg.byPower(e) == true) {
					// Increase zone population
					reg.incCellPop(e);
				}
				//If zone is adjacent to 1+ zones with a population of 1
				else if (reg.adjPop(1, e) >= 1) {
					// Increase zone population
					reg.incCellPop(e);
				}
			} else if (reg.cellPop(e) == 1) {	// If zone has population of 1
				// If zone is adjacent to 2+ zones with a population of 1
				if (reg.adjPop(1, e) >= 2) {
					// Increase zone population
					reg.incCellPop(e);
				}
			} else if (reg.cellPop(e) == 2) {	// If zone has population of 2
				// If zone is adjacent to 4+ zones with population of 2
				if (reg.adjPop(2, e) >= 4) {
					// Increase zone population
					reg.incCellPop(e);
				}
			}
		}
	}

	return;
}

//RESIDENTIAL ZONE FUNCTION DEFINITIONS
Resident::Resident(){}

void Resident::ResCheck(Region &r)
{//NOTE: "ELSE" are placeholders
	int e;//To store the value of getListItem()
	//PRIORITIZE RESIDENTIAL CELLS FOR POPULATION INCREASE
	r.prioritizeCells('R');

	for(int i = 0; i < r.cellListSize(); i++)//Check Every cell in the Array
	{
		//SET ELEMENT
		e = r.getListItem(i);
		//POPULATION GROWTHS
		if(r.cellPop(e) == 0)
		{
			if(r.byPower(e) == true)
			{
				r.incCellPop(e);//IF THERE IS A POWERLINE NEXT TO IT,GROW
			}
			else if(r.adjPop(1,e) >= 1)
            {
				r.incCellPop(e);//IF THERE IS AT LEAST 1 ADJ WITH "1+",GROW
            }
		}
		else if(r.cellPop(e) == 1)
		{
            if(r.adjPop(1,e) >= 2)
            {
				r.incCellPop(e);//IF THERE IS AT LEAST 2 ADJ WITH "1+",GROW
            }
		}
		else if(r.cellPop(e) == 2)
        {
            if(r.adjPop(2,e) >= 4)
            {
				r.incCellPop(e);//IF THERE IS AT LEAST 4 ADJ WITH "2+",GROW
            }
		}
		else if(r.cellPop(e) == 3)
        {
            if(r.adjPop(3,e) >= 6)
            {
				r.incCellPop(e);//IF THERE IS AT LEAST 6 ADJ WITH "3+",GROW
			}
        }
		else if(r.cellPop(e) == 4)
        {
            if(r.adjPop(4,e) >= 8)
            {
				r.incCellPop(e);//IF THERE IS AT LEAST 8 ADJ WITH "4+",GROW
            }
        }
	}

	return;
}
