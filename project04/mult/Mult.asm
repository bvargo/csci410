// This file is part of the materials accompanying the book
// "The Elements of Computing Systems" by Nisan and Schocken,
// MIT Press. Book site: www.idc.ac.il/tecs
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// initialize the result, RAM[2]
@2
M = 0

// Add RAM[0] to RAM[2], RAM[1] times
(LOOP)
   // if RAM[1] is 0, goto END
   @1
   D = M
   @END
   D;JEQ

   // load RAM[2] into D
   @2
   D = M

   // add RAM[0] to D
   @0
   D = D + M

   // store D to RAM[2]
   @2
   M = D

   // decrement RAM[1] by 1
   @1
   MD = M - 1

   // if D (counter) is not 0, jump to loop; else, fall through to END
   @LOOP
   D;JNE
(END)
