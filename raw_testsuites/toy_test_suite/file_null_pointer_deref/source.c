#include <stdio.h>
#include <string.h>

#define BUFFER_SIZE 16

int main(int argc, char *argv[]) {

  FILE *file_descriptor;
  char buffer[BUFFER_SIZE];
  int *null_pointer = NULL;

  if (argc != 3)
    return 1;

  if (strcmp(argv[1], "--file") == 0) {
    file_descriptor = fopen(argv[2], "r");
    fread(buffer, BUFFER_SIZE, 1, file_descriptor);
    fclose(file_descriptor);

    if (buffer[0] == 'y') {
      *null_pointer = 0;
    }
  }

  return 0;
}