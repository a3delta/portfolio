#ifndef DATAMAN_H
#define DATAMAN_H

//INCLUDES
#include <fstream>
#include <string>
using namespace std;

//CLASS DECLARATIONS

//Base class for cell data
class Cell {
    private:
        char zone;      //zoning value for cell
        int x;          //x coordinate for cell
        int y;          //y coordinate for cell
        int pop;        //population value for cell
        int apop;       //value of total pop adjacent to cell
        int poll;       //pollution value for cell
        bool updated;   //value to check if cell has been updated in current time step

    public:
        //Contructor - no destructor since nothing is dynamic
        Cell();

        //Functions to set zoning and coordinate values
        //Should not be called after child initialization
        void setZone(char c);
        void setCoord(int a, int b);
        void setUpdated(bool b);

        //Function to increase pop and adj pop by 1 and set pollution
        void incPop();
        void incAPop();
        void setPoll(int p);

        //Functions to return cell values
        char getZone();
        int getx();
        int gety();
        int getPop();
        int getAPop();
        int getPoll();
        bool getUpdate();

        //Functions to clone cell values - only used in Region cloning function
        void clonePop(int p);
        void clonePoll(int p);

};

//Class for region data using cell base class
class Region {
    private:
        Cell* c;        //cell class ptr for dynamic alloc of data
        int xMax;       //max x value for region limits
        int yMax;       //max y value for region limits
        int workers;    //available worker count
        int goods;      //avialable goods count
        int listSize;	//size of cell list
		int* cellList;	//list of cells to increase the population of

        //Function to find adjacent cell mins and maxes
        void adjBounds(int &aMin, int &aMax, int &bMin, int &bMax, int i);

        //Functions to resize the cellList array
        void resizeList(int n);     //add n elements to array
        void resetList();           //resets array to 0 elements

    public:
        //Contructor and destructor
        Region(int cnt, string* d);
        ~Region();

        //Functions to set values for workers and goods
        void incWorkers();      //increases workers by 1
        void decWorkers(int a); //decreases workers by a
        void incGoods();        //increases goods by 1
        void decGoods();        //decreases goods by 1

        //Functions to update pollution values - call after industrial func has run
        void incPoll(int inc);
        void updatePoll();

        //Function to get the highest pop value of the input zone type
        int getHiPop(char c, int &count, int last);

        //Functions to get values for workers, goods, and max x and y values
        int getWorkers();       //returns available worker count
        int getGoods();         //returns available goods count
        int getxMax();          //returns xMax value
        int getyMax();          //returns yMax value

        //Function to get upper bound for an interation loop through cells
        int cellCount();        //returns the total number of cells in region
        int cellListSize();     //returns the listSize for cellList loops

        //Functions to check cell values through region obj
        char cellZone(int inc);         //returns zoning value of cell at inc
        int cellPop(int inc);           //returns population of cell at inc
        bool cellUpdated(int inc);      //returns if cell was updated in time step
        int getListItem(int inc);       //returns cell location in array at list element inc

        //Functions to check and adjust adjacency values
        bool byPower(int inc);          //returns true if next to power
        int adjPop(int p, int inc);     //returns n adj with pop of p+
        void incAdjPop(int inc);        //increases apop value for adj cells when pop increases

        //Function to reset all cell's updated value
        //Call after zone functions in main() time loop
        void resetUpdate();

        //Function to prioritize population increases
        void prioritizeCells(char z);
        
        //increase population of a certain cell
		void incCellPop(int inc);

        //Functions to print region states
        void printRegState();   //prints region state
        void printPollState();  //prints pollution state

        //Function to print region analysis
        //Takes min x,y (a1,b1) and max x,y (a2,b2) coords
        void printAnalysis(int a1, int b1, int a2, int b2);

        //Function to validate input x,y coords
        int validateCoord(int a1, int b1, int a2, int b2);

        //Function to clone region for comparisons to the previous state
        void cloneRegion(int &prevW, int &prevG, int* prevP);

        //Function to compare the region to the previous state
        bool isEqual(int prevW, int prevG, int prevP[]);     //returns true if clone == current region

};


//OTHER FUNCTION PROTOTYPES

//Function to validate config file input
int validateConfig(string fname, string* f);

//Function to find line count in region csv for allocation
int countRegionCSV(string fname);

//Function to open region csv and pull contents
void openRegionCSV(string fname, int cnt, string* f);


#endif
