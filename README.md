
Unix Shell Assistant

The project aims at creating a assitant that could be used by beginners to get the exact commands when the query is submitted in natural language.

The project extracts the intent of the user using NLTK, SpaCy and TextBlob natural language processing toolkits. The intent is used to find all the revlant commands, then they are ranked using Page Content Ranking algorithm to find the exact command.

The man page of the obtained command is parsed to display the exact information.

The user can also provide feedback to improve the results of the assistant.
