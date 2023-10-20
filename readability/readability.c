#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int count_letters(string text);
int count_words(string text);
int count_sentences(string text);

int main(void)
{
    string text;
    int letters;
    int words;
    int sentences;
    int index;
    double L, S;

    text = get_string("Text:");

    letters = count_letters(text);
    words = count_words(text);
    sentences = count_sentences(text);

    L = letters / (float) words * 100;
    S = sentences / (float) words * 100;

    index = round(0.0588 * L - 0.296 * S - 15.8);

    if (index > 16)
        printf("Grade 16+\n");
    else if (index < 1)
        printf("Before Grade 1\n");
    else
        printf("Grade %i\n", index);
}

int count_letters(string text)
{
    int length, count = 0;

    length = strlen(text);

    for (int i = 0; i < length; i++)
    {
        if (isalpha(text[i]) != 0)
        {
            count++;
        }
    }
    // printf("%i letters\n", count);
    return count;
}

int count_words(string text)
{
    int length, count = 0;

    length = strlen(text);

    for (int i = 0; i < length; i++)
    {
        if (text[i] == ' ')
        {
            count++;
        }
    }
    count++;

    // printf("%i words\n", count);
    return count;
}

int count_sentences(string text)
{
    int length, count = 0;

    length = strlen(text);

    for (int i = 0; i < length; i++)
    {
        if (text[i] == '.' || text[i] == '!' || text[i] == '?')
        {
            count++;
        }
    }

    // printf("%i sentences\n", count);
    return count;
}
