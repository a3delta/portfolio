#ifndef REGION
#define REGION

//INCLUDES
#include <fstream>
#include <string>
#include <vector> 
using namespace std;

//CLASS DECLARATIONS


//Class for region data using cell base class
class Region {
    private:
		vector<int> populations;
		int infectedArea;			
		int infectiousPeriod;
		int contactRate;
		int vaccineNumber;
		int mSize;
		
		//matrix storing adjacency value
		vector<vector<int>> adjMatrix;
	
    public:
        //Contructor and destructor
        Region(string *f, int lCount);
        //~Region();
		
		//adjaceny checks
		void fillAdjacenyMatrix(string* f);									//fill up adjacney matrix (RUN FIRST)
		bool adjacenyCheckSpecific(int a, int b);							//checks if a is adjacent to b
		
		//calulate closeness centrallity for specfic area
		int distanceNumber(int a, int b);
		double getCCentrality(int area);
		
		//prints
		void printAllA();								//print list of adjacents for all values (check output example)
		void printPopulations();						//print list of populations
		
		
		//accessors (gets)
		int getAreaCount(){return populations.size();}
		int getPopulationAt(int value){return populations.at(value);}
		int getInfectedArea(){return infectedArea;}
		int getInfectiousPeriod(){return infectiousPeriod;}
		int getContactRate(){return contactRate;}
		int getVaccineNumber(){return vaccineNumber;}
		int getMSize(){return mSize;}
		int getAdjCountAt(int area){return adjMatrix[area-1].size();}
		int getAdjAt(int area, int pos){return adjMatrix[area-1][pos];}

		//mutators (sets)
		//void setPopulationAt(int value){return populations.at(value);}  //should never be needed, but can be added later
		void setInfectedArea(int ia){infectedArea = ia;}
		void setInfectiousPeriod(int ip){infectiousPeriod = ip;}
		void setContactRate(int cr){contactRate = cr;}
		void setVaccineNumber(int vn){vaccineNumber = vn;}
};


//OTHER FUNCTION PROTOTYPES

//Function to validate config file input
int validateConfig(string fname, string* f);

//Function to find line count in region csv for allocation
int countRegionCSV(string fname);

//Function to open region csv and pull contents
void openRegionCSV(string fname, int cnt, string* f);

#endif
