#include <stdio.h>
#define BOARD_SIZE 3

int verify_board(int board[BOARD_SIZE][BOARD_SIZE], int solution[BOARD_SIZE][BOARD_SIZE]){
 	
 	int j;
 	int k;
 	for(j=0; j<BOARD_SIZE; j++){
 		for (k=0; k<BOARD_SIZE; k++){
 			printf("PARSING: name: board value:%d address:%p line:10\n", board[j][k], &(board[j][k]));
 		}
 	}

 	int l;
 	int m;
 	for(l=0; l<BOARD_SIZE; l++){
 		for (m=0; m<BOARD_SIZE; m++){
 			printf("PARSING: name: solution value:%d address:%p line:18\n", solution[l][m], &(solution[l][m]));
 		}
 	} 	

 	int validity[BOARD_SIZE][BOARD_SIZE];
 	int q;
 	int s;
 	for(q=0; q<BOARD_SIZE; q++){
 		for (s=0; s<BOARD_SIZE; s++){
 			printf("PARSING: name: validity value:%d address:%p line:27\n", validity[q][s], &(validity[q][s]));
 		}
 	} 	

	int idx, subidx, comp;
	printf("PARSING: name: idx value:%d address:%p line:32\n", idx, &idx);
	printf("PARSING: name: subidx value:%d address:%p line:33\n", subidx, &subidx);
	printf("PARSING: name: comp value:%d address:%p line:34\n", comp, &comp);
	for (idx = 0; idx < BOARD_SIZE; idx++) {
		printf("PARSING: name: idx value:%d address:%p line:36\n", idx, &idx);
		for (subidx = 0; subidx < BOARD_SIZE; subidx++) {
			printf("PARSING: name: subidx value:%d address :%p line:38\n", subidx, &subidx);
			// Compare to rest of the row:
			for (comp = 0; comp < BOARD_SIZE; comp++) {
				printf("PARSING: name: comp value:%d address:%p line:41\n", comp, &comp);
				if (comp != subidx) {
					if (board[idx][subidx] == board[idx][comp]) {
						validity[idx][subidx] = 0;
						printf("PARSING: name: validity value:%d address:%p line:45\n", validity[idx][subidx], &(validity[idx][subidx]));
						break;
					} else {
						validity[idx][subidx] = 1;
						printf("PARSING: name: validity: value:%d address:%p line:49\n", validity[idx][subidx], &(validity[idx][subidx]));
					}
				}
			}

			if (validity[idx][subidx] != 0) {
				// Compare to rest of the column:
				for (comp = 0; comp < BOARD_SIZE; comp++) {
					printf("PARSING: name: comp value:%d address:%p line:57\n", comp, &comp);
					if (comp != idx) {
						if (board[idx][subidx] == board[comp][subidx]) {
							validity[idx][subidx] = 0;
							printf("PARSING: name: validity value:%d address:%p line:61\n", validity[idx][subidx], &(validity[idx][subidx]));
							break;
						} else {
							validity[idx][subidx] = 1;
							printf("PARSING: name: validity value:%d address:%p line:65\n", validity[idx][subidx], &(validity[idx][subidx]));
						}
					}
				}
			}
		}
	}

	/* begin test */
	int x, y;
	printf("PARSING: name: x value:%d address:%p line:75\n", x, &x);
	printf("PARSING: name: y value:%d address:%p line:76\n", y, &y);
	for (x = 0; x < BOARD_SIZE; x++) {
		printf("PARSING: name: x value:%d address:%p line:78\n", x, &x);
 		for (y = 0; y < BOARD_SIZE; y++) {
 			printf("PARSING: name: y value:%d address:%p line:80\n", y, &y);
			if (validity[x][y] != solution[x][y]) {
				printf("PARSING: --RETURN-- name: BOARD_SIZE value:%d line:82\n", BOARD_SIZE); //We won't show address of things we're returning!
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

	int i, j;
	for (i=0; i<BOARD_SIZE; i++) {
		for(j=0; j<BOARD_SIZE; j++) {
			printf("PARSING: name: board value:%d address:%p line:100\n", board[i][j], &(board[i][j]));
		}
	}

	int solution[BOARD_SIZE][BOARD_SIZE] = 
		{{0, 1, 1},
		 {0, 1, 0},
		 {0, 1, 0}};

	int l, m;
	for (l=0; l<BOARD_SIZE; l++) {
		for(m=0; m<BOARD_SIZE; m++) {
			printf("PARSING: name: solution value:%d address:%p line:112\n", solution[l][m], &(solution[l][m]));
		}
	}

	if (verify_board(board, solution) == -1) {
		printf("2575A\n");
	} else {
		printf("failed test on BOARD_SIZE %d\n", BOARD_SIZE);
	}
    
	int board2[BOARD_SIZE][BOARD_SIZE] = 
		{{1, 2, 3},
		 {2, 3, 1},
		 {3, 1, 2}};

	int n, o;
	for (n=0; n<BOARD_SIZE; n++) {
		for(o=0; o<BOARD_SIZE; o++) {
			printf("PARSING: name: solution value:%d address:%p line:130\n", board2[n][o], &(board2[n][o]));
		}
	}

	int solution2[BOARD_SIZE][BOARD_SIZE] = 
		{{1, 1, 1},
		 {1, 1, 1},
		 {1, 1, 1}};

	int p, q;
	for (p=0; p<BOARD_SIZE; p++) {
		for(q=0; q<BOARD_SIZE; q++) {
			printf("PARSING: name: solution value:%d address:%p line:142\n", solution2[p][q], &(solution2[p][q]));
		}
	}

	if (verify_board(board2, solution2) == -1) {
		printf("2575B\n");
	} else {
		printf("failed test on BOARD_SIZE %d\n", BOARD_SIZE);
	}
    
	return 0;
}