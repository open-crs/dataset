#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>

#define CHECKED_ENV_VARIABLE "ZSH"
#define OPENED_FILE "/etc/passwd"
#define BUFFER_SIZE 16

int main(int argc, char *argv[]) {

    FILE *file_descriptor;
    char *env_var;
    char buffer[BUFFER_SIZE];
    int another_file_descriptor, dummy_number;

    // Check the environment variables
    env_var = getenv(CHECKED_ENV_VARIABLE);

    // Open a file via libcall
    file_descriptor = fopen(OPENED_FILE, "r");
    fread(buffer, BUFFER_SIZE, 1, file_descriptor);
    fclose(file_descriptor);

    // Open a file via syscall
    another_file_descriptor = open(OPENED_FILE, O_RDONLY);
    read(another_file_descriptor, buffer, BUFFER_SIZE);
    close(another_file_descriptor);

    // Check and retrieve the arguments
    if (argc == 2)
        buffer[0] = argv[0][0];

    // Read some input from the user via libcall
    printf("Gimme two lines of input:\n");
    scanf("%d", &dummy_number);

    // Read another input via syscall
    read(0, buffer, BUFFER_SIZE);

    // Dummy recv, only to have it linked
    recv(-1, NULL, 1, 0);

    return 0;
}
