#ifndef DISTRO_H
#define DISTRO_H

//INCLUDES
#include "region.h"
#include <iostream>
#include <vector>
#include<string>
#include<list>
using namespace std;

//DISTRIBUTION CLASS
class Distro{
    private:
        //VARIABLES
        vector<int> sus;        //total susceptible for each area, vector to separate areas
        vector<int> inf;        //total infectious for each area, vector to separate areas
        vector<int> rec;        //total recovered for each area, vector to separate areas
        vector<int> vac;        //total vaccinated for each area, vector to separate areas
        int pInf;               //for the peak infectious total
        int pDay;               //for the peak infectious day
        int fDay;               //for the final day of the outbreak
        int totInf;             //for the total number of agents infected during outbreak
		
		//CENTRALITY/DEGREE VARIABLES
		list<int> sort; 		//The sorted order for distributions and printing
		list<int> sortID;       // Saves the ID for the sorted items
		list<double> sortD;     //Saves degree values for sorting and printing


    public:
        //FUNCTIONS

        //CONSTRUCTOR
        Distro(Region reg);

        //CLOSENESS VACCINE DISTRIBUTION
		void cent(Region r);	//vaccines based on "DISTANCE"

        //DEGREE VACCINE DISTRIBUTION
		void deg(Region r);		//vaccines based on "DEGREES"

        //RANDOM VACCINE DISTRIBUTION
		void rand(Region r);		// "RANDOM" distribution

        //EQUAL VACCINE DISTRIBUTION
		void equ(Region r);		// "EQUAL" distribution

        //CONTAGION EXPERIMENT
        void experiment(Region reg);

        //EXPERIMENT ANALYSIS
        void printResult(string name);

};

#endif
