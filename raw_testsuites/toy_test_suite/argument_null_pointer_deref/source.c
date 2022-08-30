#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
  int *null_pointer = NULL;

  if (argc != 3)
    return 1;

  if (strcmp(argv[1], "--string") == 0) {
    if (argv[2][0] == 's') {
      *null_pointer = 0;
    }
  }

  return 0;
}