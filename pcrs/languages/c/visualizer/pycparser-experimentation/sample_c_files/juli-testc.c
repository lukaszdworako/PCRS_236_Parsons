#include <stdio.h>
#define BOARD_SIZE 3

int verify_board(int board[BOARD_SIZE][BOARD_SIZE], int solution[BOARD_SIZE][BOARD_SIZE]){
 	
 	int j;
 	int k;
 	for(j=0; j<BOARD_SIZE; j++){
 		for (k=0; k<BOARD_SIZE; k++){
 			printf("PARSING: name: board value:%d address:%p\n", board[j][k], &(board[j][k]));
 		}
 	}

 	int l;
 	int m;
 	for(l=0; l<BOARD_SIZE; l++){
 		for (m=0; m<BOARD_SIZE; m++){
 			printf("PARSING: name: solution value:%d address:%p\n", solution[l][m], &(solution[l][m]));
 		}
 	} 	

 	int validity[BOARD_SIZE][BOARD_SIZE];

	int idx, subidx, comp;
	for (idx = 0; idx < BOARD_SIZE; idx++) {
		for (subidx = 0; subidx < BOARD_SIZE; subidx++) {
			// Compare to rest of the row:
			for (comp = 0; comp < BOARD_SIZE; comp++) {
				if (comp != subidx) {
					if (board[idx][subidx] == board[idx][comp]) {
						validity[idx][subidx] = 0;
						break;
					} else {
						validity[idx][subidx] = 1;
					}
				}
			}

			if (validity[idx][subidx] != 0) {
				// Compare to rest of the column:
				for (comp = 0; comp < BOARD_SIZE; comp++) {
					if (comp != idx) {
						if (board[idx][subidx] == board[comp][subidx]) {
							validity[idx][subidx] = 0;
							break;
						} else {
							validity[idx][subidx] = 1;
						}
					}
				}
			}
		}
	}

	/* begin test */
	int x, y;

	for (x = 0; x < BOARD_SIZE; x++) {
 		for (y = 0; y < BOARD_SIZE; y++) {
			if (validity[x][y] != solution[x][y]) {
				return BOARD_SIZE;
			}
		}
	}

	return -1;
}

int main() {
	int board[BOARD_SIZE][BOARD_SIZE] = 
		{{1, 2, 3},
		 {1, 3, 2},
		 {2, 1, 2}};

	int solution[BOARD_SIZE][BOARD_SIZE] = 
		{{0, 1, 1},
		 {0, 1, 0},
		 {0, 1, 0}};

	if (verify_board(board, solution) == -1) {
		printf("2575A\n");
	} else {
		printf("failed test on BOARD_SIZE %d\n", BOARD_SIZE);
	}
    
	int board2[BOARD_SIZE][BOARD_SIZE] = 
		{{1, 2, 3},
		 {2, 3, 1},
		 {3, 1, 2}};

	int solution2[BOARD_SIZE][BOARD_SIZE] = 
		{{1, 1, 1},
		 {1, 1, 1},
		 {1, 1, 1}};

	if (verify_board(board2, solution2) == -1) {
		printf("2575B\n");
	} else {
		printf("failed test on BOARD_SIZE %d\n", BOARD_SIZE);
	}
    
	return 0;
}