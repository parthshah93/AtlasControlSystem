void initIndicators(){
	unsigned char i;
	for(i = 22; i < 29; i++){
		pinMode(i, OUTPUT);
		digitalWrite(i, LOW);
	}
	
}

void 