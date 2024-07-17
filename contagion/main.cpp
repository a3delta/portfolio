//===========================================================
//Project 2: Contagion
//Description:
//  Design and implement a system in C/C++
//  that will simulate the effectivness of vaccines
//  following different distribution patterns
//===========================================================

#include "region.h"
#include "distro.h"
#include <fstream>
#include <iostream>
#include <string>
#include <vector> 
using namespace std;

int main(){

    //GENERIC VARIABLES
    int valid;            	  	//for validity check
    int lCount;              	//for counting lines in file
    int er=0;              		//for exiting bad input loops
	int parse;					//for parsing through adjArray
	
	int arrayTemp[10];				//tests
	int finalSpot;

    //FILE OPERATION VARIABLES
    string conFile;             //for config file name input
    string* fc = new string[7]; //for config file contents
    string* region = NULL;      //for region csv file contents

    //TIME VARIABLES
    int day = 0;

	//OUTPUT THE BEGINNING OF THE SIM
    cout << "Beginning simulation" << endl;


	//PROMPT USER FOR CONFIG FILE

    //while loop to loop in the event of bad config file input
    while(valid != 1){

        //prompt for config file input
        cout << "Please enter the name of the configuration file: ";
        cin >> conFile;

        //test input validity
        valid = validateConfig(conFile, fc);

    }
	
	//LOAD REGION LAYOUT FROM CSV IN CONFIG

    //get the line count for region csv for allocation
    lCount = countRegionCSV(fc[0]);
	//cout << endl << lCount << endl;
	
	//allocate memory for matrix csv contents, and turn into a manipulatable string
    region  = new string[lCount+1];
	
	

    //open region csv and store in string array
    openRegionCSV(fc[1], (lCount), region);
	
	//construct region object
	Region r = Region(fc, lCount);
	
	//make adjaceny matrix
	r.fillAdjacenyMatrix(region);
	
	//---------------------------------
	//---------SETUP COMPLETE----------
	//---------------------------------

    //OUPUT THE INITIAL DATA

    //output the initial population of each area
    cout << "Regional Population" << endl;
    r.printPopulations();

    //output the adjacency list
    cout << "Adjacency List" << endl;
    r.printAllA();

    //SETUP OBJECTS FOR DISTRIBUTION AND EXPERIMENT
	
    //4 distribution strategies objects
    Distro cent = Distro(r);
    Distro deg = Distro(r);
    Distro rand = Distro(r);
    Distro equ = Distro(r);

    //RUN DISTRIBUTIONS
    cent.cent(r);
    deg.deg(r);
    rand.rand(r);
    equ.equ(r);


    //RUN EXPERIMENTS FOR EACH DISTRIBUTION

    //closeness distribution experiment
    cout << "CLOSENESS DISTRIBUTION" << endl;
    cent.experiment(r);

    //degree distribution experiment
    cout << "DEGREE DISTRIBUTION" << endl;
    deg.experiment(r);

    //random distribution experiment
    cout << "RANDOM DISTRIBUTION" << endl;
    rand.experiment(r);

    //equal distribution experiment
    cout << "EQUAL DISTRIBUTION" << endl;
    equ.experiment(r);
	
	//analysis
	cent.printResult("closeness centrality");
	deg.printResult("degree centrality");
	rand.printResult("random");
	equ.printResult("equal");

	return 0;
}
