#ifndef _INDICATORS_H
#define _INDICATORS_H

class Indicator{
public:
	void setForward();
	void setBackward();
	void setLeft();
	void setRight();
	void setConnectionBreak();
	void setDig();
	void setDumping();
	void resetForward();
	void resetBackward();
	void resetLeft();
	void resetRight();
	void resetConnectionBreak();
	void resetDig();
	void resetDumping();
	unsigned char forward = 22;
	unsigned char backward = 23;
	unsigned char left = 24;
	unsigned char right = 25;
	unsigned char connectionBreak = 26;
	unsigned char dig = 27;
	unsigned char dump = 28;
};


#endif