//INCLUDES
#include "distro.h"
#include <iostream>
#include <vector>

using namespace std;

//CONSTRUCTOR
Distro::Distro(Region reg){
    //resize each vector
    sus.resize(reg.getAreaCount());
    inf.resize(reg.getAreaCount());
    rec.resize(reg.getAreaCount());
    vac.resize(reg.getAreaCount());

    //set agent total counts
    for(int i=0; i<reg.getAreaCount(); i++){
        sus.at(i) = reg.getPopulationAt(i);
        inf.at(i) = 0;
        rec.at(i) = 0;
        vac.at(i) = 0;
    }

    //set other variables
    pInf = 0;       //default to 0
    pDay = 0;       //patient 0 is infectious on day 0
	fDay = 0;		//defaulting to 0
	totInf = 0;		//defaulting to 0

}

//CLOSENESS VACCINE DISTRIBUTION
void Distro::cent(Region r)//vaccines based on "CLOSENESS"
{
	//SORTING VARIABLES
	vector<double> temp1;		//for managing closeness relation to area
	vector<double> temp2;		//for managing closeness relation to area
	vector<int> tempID1;		//for managing closeness relation to area
	vector<int> sorted;			//for the prioritized areas
	vector<int> vis;			//to exclude visited areas
	bool visited = false;		//to exclude visited 
	
	//VACCINE DISTRIBUTION VARIABLES
	int totalvax = r.getVaccineNumber();

	for(int i = 1;i <= r.getMSize();i++){
		//get centralities in order from area 1 to area mSize
		temp1.push_back(r.getCCentrality(i));
		sortD.push_back(r.getCCentrality(i));
		tempID1.push_back(i);
	}

	//now sort
	sortD.sort();

	//convert sortD list into a vector for easy direct element access
	for(list<double>::iterator it=sortD.begin(); it != sortD.end(); ++it){
		temp2.push_back(*it);
	}

	//sort array of areas in order of closeness
	for(int i=0; i<r.getMSize(); i++){
		//for each element in unsorted array temp1
		for(int j=0; j<tempID1.size(); j++){
			if(temp1[j] == temp2[i]){
				//verify that area has not been visited/compared already
				for(int k=0; k<vis.size(); k++){
					if(vis[k] == tempID1[j]){
						visited = true;
					}
				}
				if(visited != true){
					//if not visited, push equivalent area ID into sorted list and add to visited
					sorted.push_back(tempID1[j]);
					vis.push_back(tempID1[j]);
					//exit loop to avoid duplicates
					j += r.getMSize();
				}
				//reset visited
				visited = false;
			}
		}
	}

	//distribute vaccines
	for(int i=0; i<sorted.size(); i++){
		//if total pop for area at sorted[i] <= totalvax, assign amount = to total pop
		if(r.getPopulationAt(sorted[i]-1) <= totalvax){
			vac[sorted[i]-1] = r.getPopulationAt(sorted[i]-1);
			totalvax -= r.getPopulationAt(sorted[i]-1);
		}
		//else, assign the remaining vax
		else{
			vac[sorted[i]-1] = totalvax;
			totalvax = 0;
		}
		//exit loop
		if(totalvax == 0){
			i = sorted.size();
		}
	}

}


//DEGREE VACCINE DISTRIBUTION
void Distro::deg(Region r)//vaccines based on "DEGREES"
{
	int lastLocation = -1;

	for(int i = 1;i <= r.getMSize();i++)
        {
		sort.push_back(r.getAdjCountAt(i));
	}
	//vaccine priority 
	sort.sort();
	sort.reverse();
	//cout << "SORTED\n";
	for(auto i = sort.begin();i != sort.end();i++)
	{
		bool check = false;

		//only run if value has not been visited before
		if (lastLocation != *i)
		{
			for(int j = 1;j <= sort.size();j++)
			{
				if(r.getAdjCountAt(j) == *i && check == false)
				{
					//cout << "ID: " << j << " Degree: " << *i << endl;
					sortID.push_back(j);
				}
			}
		}
		lastLocation = *i;
	}
	
	//distribute vaccines
	int vacNum = r.getVaccineNumber();
	int currentPopulation = 0;
	
	//loop through adding vaccines to area
	for(auto i = sortID.begin();i != sortID.end();i++)
	{
		//see what pop is for area
		currentPopulation = r.getPopulationAt(*i-1);
		
		//add total pop worth of vaccines if possible
		if (currentPopulation <= vacNum){
			vac[*i-1] = currentPopulation;
			vacNum -= currentPopulation;
		} else if (currentPopulation > vacNum){
			vac[*i-1] = vacNum;
			vacNum = 0;
		}
	}
	
}


//RANDOM VACCINE DISTRIBUTION
void Distro::rand(Region r) {
	int vaxxLeft = r.getVaccineNumber();		// Initial vaccine number

	// cout << vaxxLeft << endl;

	for (int i = 0; i < r.getAreaCount(); i++) {
		if (vaxxLeft >= r.getPopulationAt(i)) {	// Checks if there is enough vaccines to fulfill the entire area's population
			vac.at(i) = r.getPopulationAt(i);	// Distribute vaccine equal to population number
			vaxxLeft -= r.getPopulationAt(i);	// Take vaccine from supply
		} else {				// If there is NOT enough vaccines
			vac.at(i) = vaxxLeft;		// Distribute what's left
			vaxxLeft -= vaxxLeft;
		}

		// cout << vac.at(i) << endl;
	}
}

//EQUAL VACCINE DISTRIBUTION
void Distro::equ(Region r) {
	int vaxxLeft = r.getVaccineNumber();		// Initial amount

	while (vaxxLeft > 0) {				// Doesn't stop until out of vaccines
		for (int i = 0; i < r.getAreaCount(); i++) {
			if (vac.at(i) < r.getPopulationAt(i) && vaxxLeft > 0) { // Caps at max population and 0 vaccines
				vac.at(i) += 1; // Give 1 vaccine to each area
				vaxxLeft--;	// Remove 1 vaccine from supply for each area
			}
		}
	}
}

//CONTAGION EXPERIMENT
void Distro::experiment(Region reg){
	int tInfect = 1;			//total infectious, default is 1 for patient 0
	int day = 0;				//day number, default is 0
	int areaCount = sus.size();	//for for loops
	int convert;				//for number of S to convert to I
	vector<vector<int>> ia;		//for tracking infectious period for I agents in specific areas
	int ip;						//for infectious period value
	vector<int> spread;			//for making sure fresh spread isnt updated early

	//set patient 0
	if(vac.at(reg.getInfectedArea() - 1) < sus.at(reg.getInfectedArea() - 1)){
    	inf.at(reg.getInfectedArea()-1) = 1;
		sus.at(reg.getInfectedArea()-1) -= 1;
	}

	//initialize infectious agent data, first push is patient 0
	ip = reg.getInfectiousPeriod();
	ia.resize(areaCount);
	if(inf[reg.getInfectedArea()-1] != 0){
		ia[reg.getInfectedArea()-1].push_back(ip);
	}

	//subtract V agent count from the S agent count
	for(int i=0; i<areaCount; i++){
		sus[i] -= vac[i];
	}

	//daily simulation loop
	while(tInfect != 0){

		//output the current day number, then increment the day
		cout << "Day " << day << endl;
		day++;

		//reset tInfect to 0 for for loop calculation
		tInfect = 0;

		//for each area, print the data
		for(int i=0; i<areaCount; i++){

			//output the area ID, total population and number of SIRV agents
			//need to manage formatting
			cout << (i+1) << "\tPOP: " << reg.getPopulationAt(i) << "\t";
			cout << "S: " << sus[i] << "\tI: " << inf[i] << "\t";
			cout << "R: " << rec[i] << "\tV: " << vac[i] << endl;

		}

		//for each area, spread virus if I > pop/2
		for(int i=0; i<areaCount; i++){

			//count the total number of infectious for the day
			tInfect += inf[i];

			//for each infectious agent, decrement their infectious period value
			if(ia[i].size() > 0){
				for(int j=0; j<ia[i].size(); j++){
					ia[i][j] -= 1;
				}
			}

			//if the total infections are > the current peak
			if(tInfect > pInf){
				//store the day and the total as the peak, then continue
				pInf = tInfect;
				pDay = day - 1;
			}

			//if the number of I agents are > the areas pop/2
			if( inf[i] > (reg.getPopulationAt(i) / 2) ){

				//convert 1 S agent in an adjacent area into an I if they have 0 I
				for(int j=0; j<reg.getAdjCountAt(i+1); j++){
					//only allow spread if S > 0 and I == 0
					if( (sus[reg.getAdjAt(i+1, j)-1] > 0) && (inf[reg.getAdjAt(i+1, j)-1] == 0) ){
						inf[reg.getAdjAt(i+1, j)-1] += 1;
						sus[reg.getAdjAt(i+1, j)-1] -= 1;
						spread.push_back(reg.getAdjAt(i+1, j));
					}

					//manage adjacent list, always size 8 and has 0 for empty space
					//if(reg.getAdjAt(i+1, (j+1)) == 0){
					//	j += reg.getAdjCountAt(i+1);
					//}
				}
			}

			//of available S agents, convert I * contact rate into I agents
			convert = inf[i] * reg.getContactRate();

			//manage fresh spread
			for(int j=0; j<spread.size(); j++){
				if((i+1) == spread[j]){
					convert -= reg.getContactRate();
				}
			}

			//if num to convert is < num of S
			if( (convert < sus[i]) && (convert > 0) ){
				//add the new I agents to ia
				for(int j=0; j<convert; j++){
					ia[i].push_back(ip);
				}
				//convert num to convert from S to I
				inf[i] += convert;
				sus[i] -= convert;
			}
			//else, convert is >= S
			else if(convert >= sus[i]){
				//add the new I agents to ia
				for(int j=0; j<sus[i]; j++){
					ia[i].push_back(ip);
				}
				//so convert all remaining S to I
				inf[i] += sus[i];
				sus[i] = 0;
			}

			//if any Is infectious period has been decremented to 0
			for(int j=0; j<ia[i].size(); j++){
				if( (ia[i][j] <= 0) && (ia[i].size() > 0) ){
					//convert those I's to R's
					rec[i] += 1;
					inf[i] -= 1;
				}
			}

			//clean up ia, delete the first element because ia is in FIFO order
			if(ia[i].size() > 0){
				while( (ia[i][0] == 0) && (ia[i].size() > 0) ){
					ia[i].erase( ia[i].begin() );
				}
			}

		}

		//manage infectious rate for fresh spread
		for(int i=0; i<spread.size(); i++){
			ia[spread[i]-1].push_back(ip);
		}

		//empty spread[]
		spread.erase(spread.begin(), spread.end());

		//extra endl for formatting the daily output
		cout << endl;

		//if the total number of infections for the day are 0
		if(tInfect == 0){
			//store the day as the final day of the outbreak and end
			fDay = day - 1;
			//count the total number of recovered agents and store the total
			for(int i=0; i<areaCount; i++){
				totInf += rec[i];
			}
		}

	}

	return;
}

//EXPERIMENT ANALYSIS
void Distro::printResult(string name){
	/*
	Using the closeness centrality distribution method, the peak number of infected was 6748 on day 7. The outbreak ended on day 25 and the total number of infected individuals was 16500.
	Using the degree centrality distribution method, the peak number of infected was 6748 on day 7. The outbreak ended on day 25 and the total number of infected individuals was 16500.
	Using the random distribution method, the peak number of infected was 13742 on day 14. The outbreak ended on day 24 and the total number of infected individuals was 25500.
	Using the equal distribution method, the peak number of infected was 7619 on day 22. The outbreak ended on day 32 and the total number of infected individuals was 24438.
	Using the weighted distribution method, the peak number of infected was 3436 on day 6. The outbreak ended on day 9 and the total number of infected individuals was 3500.

	int pInf;               //for the peak infectious total
    int pDay;               //for the peak infectious day
    int fDay;               //for the final day of the outbreak
    int totInf;             //for the total number of agents infected during outbreak
	*/
	//print 
	cout << "Using the " << name << " distribution method, the peak number of infected was ";
	cout << pInf << " on day " << pDay << ".";
	cout << "The outbreak ended on day " << fDay << " and the total number of infected individuals was " << totInf << ".\n";	
}


