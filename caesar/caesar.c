#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

bool only_num(string text);
char rot(char p, int k);

int main(int argc, string argv[])
{
    int k, lepl;
    string plain;
    if (argc != 2 || !only_num(argv[1]))
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    k = atoi(argv[1]);
    plain = get_string("plaintext: ");
    lepl = strlen(plain);
    char ciph[lepl + 1];
    for (int i = 0; i < lepl; i++)
    {
        ciph[i] = rot(plain[i], k);
    }
    ciph[lepl] = '\0';
    printf("ciphertext:%s\n", ciph);
    return 0;
}

bool only_num(string text)
{
    int lepl;

    lepl = strlen(text);

    for (int i = 0; i < lepl; i++)
    {
        if (!isdigit(text[i]))
        {
            return false;
        }
    }
    return true;
}
char rot(char p, int k)
{
    char pi, c, ci;
    if (isupper(p))
    {
        pi = p - 65;
        ci = (pi + k) % 26;
        c = ci + 65;
    }
    else if (islower(p))
    {
        pi = p - 97;
        ci = (pi + k) % 26;
        c = ci + 97;
    }
    else
    {
        return p;
    }
    return c;
}
