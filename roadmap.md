# Italiano project
This porject is setup to create learning ressources for learning italian. This is a brute force approach rather than grammatical approach. 

This is also to learn how to work with databases, so on my local version i will have a database that will contain all the words
## Mission
To create analog training exercises for memorising the italian top 1000 words. This will be done iteratively by focusing first on the top 100 words, and then iteratively build out from there. 
## Tools
To have a repo which can create exercise pages, these should have a series of questions and then contain the answers. the answer should be stored at the bottom in an upside down fashion so that the user can't directly read it
0. dictionary of the top 1000 most used italian words
1. translations from english to italian
   "I want an ice cream" _____ un gelato
2. translations from italian to english
3. sheets of translations, providing the english "to be" and then having to fill out the six conjugations in the given tempo
4. there wil lbe a series of static csv [based on url] which can be acccessed by any ones. so that all can access verbs, subjects under raw.github...../verbs.csv
## Steps
### Dictionary steps
#### Verbs
Most used italian tense
    Passato Prossimo -> Present Perfect
    Passato Remoto -> Historical Past
    Imperetto -> Impercet
    Present
    Futuro Semplice - Simple Future
    Condizionale Presente -> presente condtional
    Congiuntivo Presente - Present Subjuctive
1. 100 most used verbs
2. 101-200 Most
3. 201-400 

#### Subjects

#### Prepositions

####
### 

---------------------------------------------------------------- 
Database & Infrastructure

1. What type of database do you want locally? (SQLite, PostgreSQL, or
something else? Do you want it to sync with the GitHub JSON or be completely
separate?)
PostgresSQL i want to work with SQL database that i can host for free locally i think it shuold be completely separate but i would like to update the static csvs at regular intervals
2. How do you envision the CSV exports working? (Should they be
auto-generated from the dictionary, manually curated, or both? What's the exact URL structure you want for raw.github.../verbs.csv?)
the csv exports should be csv files that live in this repo, but that is then updated at regular intervals when i work with the data or update it. so we need scripts which update the csvs inside of the file at regular intervals.

Exercise Generation

3. What specific question formats do you want for the translation exercises?
(Multiple choice, fill-in-the-blank, or just write the translation? Any image support for visual learners?)
All of the above, ideally the answers should be present at intervals. Images are not included as they would be require more deveelopement. maybe emojies can be used
4. For conjugation sheets, what layout do you prefer? (Table format with all
6 persons, or individual blanks like "io _____, tu _____, lui/lei _____"?)
table format to compact it as much as possible

Content Prioritization
5. Should we focus on completing all tenses for the current 7 verbs first, or add more verbs with basic tenses? (Quality vs quantity approach for the 100 most used verbs?)
Yes, we shuold build it iteratively
6. What criteria should determine the "top 1000" words? (Frequency in spoken Italian, written Italian, or a specific corpus like news/conversation?)
that is frequency above all else ideally in spoken italian, but ill take wahte ever proxy i need
Brute Force vs Grammar

7. How "brute force" do you want this? (Pure memorization drills, or should we include minimal grammar explanations for context, especially for irregular verbs?)
memorisation above all in the beginning the focus is on learning how to insert words in sentences. at some point it will become about placing the
8. What's your preferred repetition strategy? (Spaced repetition intervals, random sampling, or progressive difficulty based on user performance?)
spaced repetition. ideally we want to make a method for storing the words that im good at and that im bad at.

User Experience

9. How do you want users to track their progress? (Should the system remember which words they've mastered, or keep it completely stateless with just PDF exercises?)
first prioritty is stateless, if we can solve the logging in and insertion of data than we can do this, but first and foremost randomness and stateless apges
10. What's the ideal exercise session length? (5-minute quick drills, 15-minute focused sessions, or longer comprehensive reviews? This affects how many questions per PDF.)
currently as many. as possible we want one a4 page to ahave  as many exercises as possible, with a regurlar fotn and then having the answers in a tiny grey font at the bottom. this will be an iterative process

These questions will help shape the technical architecture and learning
methodology for your Italian dictionary project! 🇮🇹