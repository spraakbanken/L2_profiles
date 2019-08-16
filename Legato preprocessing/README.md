# Legato preprocessing scripts

## 1. Creating the SenStarLex file
Use the script *coctaill_mixer_orig.py*. 

Set the *PATH* to *COCTAILL.xml*, the sense-annotated COCTAILL file.

Set the *PATH* to the output file.

The script will output a file with this format:

| lemgram | pos | sense | cefr |
| --- | --- | --- | --- |
| lemgram | pos | sense | cefr |

Where *cefr* is the CEFR level of the expression based on the *first-occurrence* mapping method.

## 2. Adding SALDO information
Use the script *sense_List_add_saldo_information.py*.

**Note**: The expected format is

| lemgram | pos | sense | cefr |
| --- | --- | --- | --- |
| lemgram | pos | sense | cefr |

Set the *PATH* to the sense list created in the first step.

Set the *PATH* to the output file.

Set the *PATH* to Saldo.

**Note**: This script requires the text version of Saldo version 2.3.

The script will output a file with this format:

| lemgram | sense | pos | primary | secondary | cefr |
| --- | --- | --- | --- | --- | --- |
| lemgram | sense | pos | primary | secondary | cefr |

Where *primary* is the primary sense descriptor from Saldo and *secondary* is the secondary sense descriptor from Saldo.

## 3. Linking lexical resources
Use the script *to_legato_local.py*.

**Note**: The expected input format is

| lemgram | sense | pos | primary | secondary | cefr |
| --- | --- | --- | --- | --- | --- |
| lemgram | sense | pos | primary | secondary | cefr |

Set the *PATH* to the Saldo-linked file created in the previous step.

Set the *PATH* to the output file.

This script will output a file with this format:

| lemgram | sense | pos | field_name | field_value |
| --- | --- | --- | --- | --- |
| lemgram | sense | pos | field_name | field_value |

Where *field_name* corresponds to a column in the SQL database and *field_value* contains the value to be inserted into the columns. For example if *field_name* equals *synonyms*, *field_value* will contain synonyms for the lemgram+sense-tuple in questions.

## 4. Linking examples
Use the script *to_legato_local_example_sentences.py*.

**Note**: The expected input format is

| lemgram | sense | pos | primary | secondary | cefr |
| --- | --- | --- | --- | --- | --- |
| lemgram | sense | pos | primary | secondary | cefr |

Set the *PATH* to the Saldo-linked file created in step 2.

Set the *PATH* to output files. Output 1 contains example sentences, while output 2 contains entries for which no examples could be found.

This script will output a file with this format:

| lemgram | sense | pos | field_name | field_value |
| --- | --- | --- | --- | --- |
| lemgram | sense | pos | field_name | field_value |

## 5. Populating the database
For performance reasons, the output from step 3 and 4 is played into the database directly on the server.
