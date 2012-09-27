/*
  exercise: Assembler practice

  operation: x<<k

  Simon Maurer
  Lothar Rubusch
  Yosafat ?
 */

#include <stdlib.h>

int f_leftshift()
{
	int x,k, res;
	x=16;
	k=2;

        /* x<<k */
	res = x<<k;

        return res;
}

int main( int argc, char** argv )
{
	f_leftshift();
	exit( EXIT_SUCCESS );
}
