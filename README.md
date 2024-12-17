# Overview

This is a little project I've been maintaining for tracking the exercises I do around the house.

To be clear, this is *not* intended for tracking an actual exercise routine (of the sort where one would go to the gym and put in headphones and work up a sweat for an hour). Rather, I have gotten into the habit of doing a few sets of pushups each day at essentially random times, and this project is for tracking and analyzing at-will calisthenics sets of that sort.

# Files

- `home_exercises.numbers`: the Apple Numbers file in which I track my exercises.
  - This file is formatted as follows:
    - The file contains one sheet for each month, formatted as `"YYYY-MMMM"`, e.g. `"2024-November"`.
    - Each sheet contains one table (the name of the table doesn't matter).
    - Each row in each table represents one set of an exercise, and each table contains the following five columns:
      - `"location"`: the location in which I performed the set (e.g. my apartment or my parents' house).
      - `"exercise"`: e.g. pushups or calf raises.
      - `"date"` and `"time"`.
      - `"count"`: the number of reps done in the set.
- `environment.yml`: environment file from which to create a conda environment in which to run the project.
  - N.B. this project relies on the package `numbers_parser`. See Notes for discussion.
- `tools.py`: a collection of functions for various analysis tasks. These include:
  - `import_month()`, to import and clean a specific month of exercises as a pandas DataFrame.
  - `exercise_projection()`, to display statistics and projections about a specific exercise for the current month (e.g. total reps done so far this month, reps per day necessary to reach a goal total by the end of the month).
  - `exercise_statistics()`, to display statistics about a specific exercise for a current or past month (e.g. total done, average reps per set, average reps per day).
  - `stacked_bar_exercise_month()`, to display daily reps of a specific exercise as a stacked bar chart (one bar per day, one sub-bar per set).
- `analysis.py`: the Jupyter notebook in which I use of the analysis functions in `tools.py`.

# Notes as of Dec 17, 2024

## What this project is and isn't suitable for

This project is not suitable for tracking weighted exercises.

This project could be used for tracking time-based exercises, e.g. planks, by using the `"count"` column to represent the number of seconds for which the exercise is performed. The major caveat here is that the time unit would be left implicit, so the user would have to maintain unit consistency themselves.

## Use of Apple Numbers

I make use of Apple Numbers for my exercise tracking because I have a MacBook. With the `numbers_parser` package this is not currently a problem -- this package allows me to import from Apple Numbers into pandas just as I would from Excel or what have you.

However there is the possibility of future compatibility problems: as Apple Numbers automatically updates, the `numbers_parser` version in `environment.yml` might become incompatible with some future version of Numbers. With the current versions of `numbers_parser` (4.14.1) and Numbers (14.3), the package generates a UserWarning stating "Numbers version 14.3 not tested with this version". I have not yet come across any problems by just ignoring this warning, but this is something to keep an eye on.
