
# Unix Shell Assistant

* The project aims to create an assistant that could be used by beginners to get the exact commands when the query is asked right in their Unix terminal in their natural language.

* The intent of the user was extracted from the natural language query of the user using NLTK, SpaCy, and TextBlob natural language processing toolkits.

* The relevant commands are searched in the inbuilt Unix man page using the extracted intent.

* The obtained man pages are ranked using the Page Ranking Algorithm to find the exact command.

* The selected page was parsed to find just the required information from the humongous man page information.

* This exact information is shown to the user.

* The user will also be given an option to leave feedback by giving a thumbs up or down for the result. This feedback is incorporated into the Page Ranking Algorithm to improve future results.

* The Unix shell assistant built right into the terminal understands the human natural language and gives the exact command with just the required information.
