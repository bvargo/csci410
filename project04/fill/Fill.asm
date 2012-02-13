// This file is part of the materials accompanying the book
// "The Elements of Computing Systems" by Nisan and Schocken,
// MIT Press. Book site: www.idc.ac.il/tecs
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed,
// the screen should be cleared.

// fill with the appropriate color based on whether the keyboard key is
// pressed
(WAITING)
   // load the current key press into D
   @KBD
   D=M

   // if D is 0, then there is no key pressed, fill with white
   // if D is not 0, then there is a key pressed, fill with black
   @FILL_BLACK
   D;JNE

   (FILL_WHITE)
   @color
   M=0
   @FILL
   0;JMP

   (FILL_BLACK)
   @color
   M=-1
   @FILL
   0;JMP

// fill with a specified color (in @color)
(FILL)
   // memory location of the current pixel is stored in address
   @SCREEN
   D=A
   @address
   M=D

   // each row is 32 16-bit bytes
   // 256 rows * 32 bytes = 8192 bytes (16 bits to a byte here) of memory
   // count down to fill
   @8192
   D=A
   @counter
   M=D

   (FILL_LOOP)
      // load the color into D
      @color
      D=M

      // deference the pointer and set to the color
      @address
      A=M
      M=D

      // increase the address by 1
      @address
      M=M+1

      @counter
      M=M-1
      D=M

      @FILL_LOOP
      D;JGT

   // done filling with the specified color
   // go back to the waiting state
   @WAITING
   0;JMP
