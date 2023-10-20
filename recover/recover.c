#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    // declaring array of 512k chunks
    typedef uint8_t byte;
    byte chunk[512];
    int count = 0;
    char name[8];
    bool foundpeg = false;
    // opening file specified in argv[1] and calling it og
    FILE *image = NULL;

    if (argc < 2)
    {
        printf("./recover filename.*");
        return 1;
    }
    FILE *og = fopen(argv[1], "r");
    // if og returns nothing then
    if (og == NULL)
    {
        // send error message
        printf("The file cannot be opened\n");
        return 1;
    }

    // loop through each chunk

    while (true)
    {
        int bread = fread(chunk, sizeof(byte), 512, og);
        // Look for the header of a jpeg
        if (chunk[0] == 0xff && chunk[1] == 0xd8 && chunk[2] == 0xff && (chunk[3] & 0xf0) == 0xe0)
        {
            // check if it's the first jpeg
            if (count == 0)
            {
                // start writing 000.jpg
                sprintf(name, "%03i.jpg", count);
                image = fopen(name, "w");
                fwrite(chunk, 1, bread, image);
                count++;
            }
            else
            {
                fclose(image);
                sprintf(name, "%03i.jpg", count);
                image = fopen(name, "w");
                fwrite(chunk, 1, bread, image);
                count++;
            }
        }
        else if (count != 0)
        {
            fwrite(chunk, 1, bread, image);
            if (bread == 0)
            {
                fclose(image);
                fclose(og);
                return 0;
            }
        }
    }
    fclose(image);
    fclose(og);
}
