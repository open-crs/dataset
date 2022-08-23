#include <stdio.h>
#include <string.h>

#define BUFFER_SIZE 16

void guess_the_pass() {}

int main() {
  char password[8];

  printf("Enter the password: ");
  gets(password);

  if (strcmp(password, "abc"))
    printf("Wrong password!\n");
  else {
    printf("Correct password, but no reward for you!\n");
  }

  return 0;
}