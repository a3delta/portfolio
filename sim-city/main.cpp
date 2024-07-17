//===========================================================
//Project 1: Sim City
//Description:
//  Design and implement a system in C/C++
//  that will simulate the growth of a city over time.
//  The simulation will cover the growth of residential,
//  commercial, and industrial zones and see how pollution
//  impacts the overall development.
//===========================================================

#include "dataMan.h"
#include "zoneFuncs.h"
#include <fstream>
#include <iostream>
#include <string>
using namespace std;

int main(){

    //GENERIC VARIABLES
    int valid;              //for validity check
    int lCount;             //for counting lines in file
    int er=0;               //for exiting bad input loops

    //FILE OPERATION VARIABLES
    string conFile;             //for config file name input
    string* fc = new string[3]; //for config file contents
    string* region = NULL;      //for region csv file contents

    //TIME VARIABLES
    int tLimit;             //time limit for sim loop
    int refRate;            //refresh rate for sim loop

    //COORDINATE VARIABLES
    int x1, x2, y1, y2;     //for user-specified regional analysis

    //COMPONENT OBJECTS
    Resident res;           //setup Resident object
    Commercial com;         //setup Commercial object
    Industrial ind;		    //setup Industrial object

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
    
    //SET TIME VARIABLES
    tLimit = stoi(fc[1]);
    refRate = stoi(fc[2]);
    
    //LOAD REGION LAYOUT FROM CSV IN CONFIG

    //get the line count for region csv for allocation
    lCount = countRegionCSV(fc[0]);

    //allocate memory for region csv contents
    region  = new string[lCount];

    //open region csv and store in string array
    openRegionCSV(fc[0], lCount, region);

    //construct region variables and setup previous state variables
    Region r = Region(lCount, region);
    int pwork = 1;      //arbitrary initialization, set to 1 to differ at start
    int pgood = 1;      //arbitrary initialization, set to 1 to differ at start
    int ppop[r.cellCount()];
    
    //de-allocate file pointers since they are no longer needed
    delete[] fc;
    delete[] region;

    //PRINT THE INITIAL REGION STATE
    cout << "Initial Region State" << endl;
    r.printRegState();
    cout << endl;

    for(int t=1; t<=tLimit; t++){

        //UPDATE REGION CLONE TO CURRENT STATE BEFORE NEXT ITERATION
        r.cloneRegion(pwork, pgood, ppop);

        //CALL COMMERCIAL FUNCTIONS
        com.growCommercial(r);

        //CALL INDUSTRIAL FUNCTIONS
	    ind.IPopCheck(r);
        r.updatePoll();

        //CALL RESIDENTIAL FUNCTIONS
        res.ResCheck(r);

        //RESET ALL REGION CELL UPDATE VALUES FOR CURRENT TIME STEP
        r.resetUpdate();

        if( !r.isEqual(pwork, pgood, ppop) ){
            //PRINT TIME STEP
            cout << "Time Step: " << t << endl;

            //PRINT AVAILABLE WORKERS AND GOODS COUNTS
            cout << "Available Workers " << r.getWorkers() << " ";
            cout << "Available Goods " << r.getGoods() << endl;

            //PRINT CURRENT REGION STATE IF REFRESH RATE IS MET
            if(( (t+1) % refRate) == 0){
                r.printRegState();
            }

            //ADD AN ENDL FOR OUTPUT FORMATTING
            cout << endl;

        }
        //ELSE, CURRENT REGION STATE IS EQUAL TO THE PREVIOUS STATE
        else{
            break;
        }

    }

    //PRINT FINAL REGION STATE
    cout << endl << "Final Region State" << endl;
    r.printRegState();
    cout << endl;

    //PRINT POLLUTION STATE
    cout << "Pollution" << endl;
    r.printPollState();

    //PRINT FULL REGION ANALYSIS
    r.printAnalysis(0, 0, r.getxMax(), r.getyMax());

    //PROMPT USER FOR COORDINATES WITHIN A LOOP FOR INPUT VALIDATION

    //re-initialize valid to 0 (false)
    valid = 0;

    //loop for validation
    while(valid != 1){

        //prompt user for coordinates for furter analysis
        cout << "Please enter the diagonal corners of the area you wish to have more information about.";
        cout << " (MinX = 0, MinY = 0, MaxX = " << r.getxMax() << ", MaxY = " << r.getyMax() << ")" << endl;

        //take user input for coordinates
        cout << "X1:";
        cin >> x1;
        cout << "Y1:";
        cin >> y1;
        cout << "X2:";
        cin >> x2;
        cout << "Y2:";
        cin >> y2;

        //validate input
        valid = r.validateCoord(x1, y1, x2, y2);

        //if invalid, output that the coordinates are invalid and loop
        if(valid == 0){
            cout << "The coordinates entered are invalid." << endl;

            //bad input loop management
            er++;
            if(er > 20){
                cout << "ERROR: Bad input. Exiting." << endl;
            	break;
            }

	    }

    }

    //PASS USER-SPECIFIED COORDINATES INTO PRINT ANALYSIS FUNCTION
    r.printAnalysis(x1, y1, x2, y2);

    //OUTPUT THE COMPLETION OF THE SIM
    cout << "Simulation complete" << endl << endl;

    return 0;
}
