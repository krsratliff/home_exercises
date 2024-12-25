import numpy as np
import pandas as pd
from numbers_parser import Document
import warnings
import calendar
from datetime import date
import matplotlib.pyplot as plt



#####################
# TOOLS FOR IMPORTING
#####################



# Import and clean a specific exercise sheet:
#   drop entirely-empty rows and columns
#   check for appropriate column names
#   check for nonemptiness of time and count columns
#   forward-fill date, location, exercise columns
#   verify that date and time can be parsed as datetimes
#   verify that count contains ints

def check_columns_existence(df):
    """Check for presence of necessary columns.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to check for necessary columns.

    Returns
    -------
    None
        Raises an error if df does not contain the columns
        "date", "time", "location", "exercise", and "count".

        Raises a warning if df contains a column other than
        those five.
    """

    # verify that the columns are correct
    col_names = {x for x in df.columns}
    col_names_req = {
        "date", "time", "location", "exercise", "count"
    }
    # if there's an extraneous column, issue warning
    if not col_names.issubset(col_names_req):
        extraneous_cols = col_names - col_names_req
        warnings.warn('Extraneous column(s) present: {}'.format(extraneous_cols))
    # if a necessary column is missing, raise an error
    if not col_names.issuperset(col_names_req):
        missing_cols = col_names_req - col_names
        raise ValueError('Required column missing: {}'.format(missing_cols))
    
    return None


def clean_exercise_sheet(df):
    """Clean the exercise records.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to check for presence and type of necessary columns.


    Returns
    -------
    pandas.DataFrame
        A pandas DataFrame containing the desired data.


    Notes
    -----
        The sheet must contain a single table (the name of
        the table doesn't matter). That table's columns 
        must be "date", "time", "location", "exercise", 
        and "count".

        The columns "date", "location", and "exercise" may 
        include empty entries; these are automatically
        forward-filled.

        The columns "time" and "count" must be entirely
        nonempty.
    """

    check_columns_existence(df)

    # check for nonemptiness of time, count columns
    for col in ["time", "count"]:
        if df[col].isna().sum() != 0:
            raise ValueError('Missing values in "{}" column'.format(col))

    # forward fill date, location, exercise
    cols_to_ffill = ["date", "location", "exercise"]
    df[cols_to_ffill] = df[cols_to_ffill].ffill()
    
    # cast "date" and "time" to datetime
    for col in ['date', 'time']:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            raise ValueError('Cannot parse "{}" column as datetime'.format(col))
        
    # cast "count" as int
    try:
        df['count'] = df['count'].astype('int')
    except:
        raise ValueError('Cannot cast "count" column to int')
    
    return df


def import_exercise_sheet(filepath, sheetname):
    """Import and clean the exercise records.
    
    The records must be in an appropriately-formatted
        Apple Numbers file. (See Notes for format.)

    Parameters
    ----------
    filepath : string
        The path to the Apple Numbers file containing the
        desired sheet.

    sheetname : string
        The name of the sheet containing the desired data.

    
    Returns
    -------
    pandas.DataFrame
        A pandas DataFrame containing the desired data.

        
    Notes
    -----
        The sheet must contain a single table (the name of
        the table doesn't matter). That table's columns 
        must be "date", "time", "location", "exercise", 
        and "count".

        The columns "date", "location", and "exercise" may 
        include empty entries; these are automatically
        forward-filled.

        The columns "time" and "count" must be entirely
        nonempty.
    """
    # import Apple Numbers file at filepath
    doc = Document(filepath)
    # obtain the specified sheet
    try:
        sheet = doc.sheets[sheetname]
    except:
        raise ValueError('Sheet name "{}" not found'.format(sheetname))

    # verify that the sheet contains only one table
    if len(sheet.tables) != 1:
        raise ValueError("Specified sheet contains >1 table")

    # obtain the values in that single table
    #   as a list of lists
    table = sheet.tables[0].rows(values_only=True)

    # store those values in a DataFrame
    df = pd.DataFrame(
        # values
        table[1:],
        # first row is column names
        columns = table[0]
    )

    # drop the entirely-empty columns and rows
    for ax in [0,1]:
        df = df.dropna(axis=ax, how='all')

    # clean the imported exercise sheet
    df = clean_exercise_sheet(df)

    return df


# Import the exercise records for a specified month
#   checks that data matches requested year and month
def import_month(filepath, year = date.today().year, month = date.today().month):
    """Import and clean the exercise records for a given
    month.
    
    The records must be in an appropriately-formatted
        Apple Numbers file.

    
    Parameters
    ----------
    filepath : string
        The path to the Apple Numbers file containing the
        desired sheet.

    year, month : int
        The year and month for which to import the data.

        Default values: current year and month.
    
       
    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the desired data.

        
    Notes
    -----
        The data must be contained in a sheet titled 
        "YYYY-MMMM", e.g. "2024-November" for year=2024 
        and month=11.

        The sheet must contain a single table (the name of
        the table doesn't matter). That table's columns 
        must be "date", "time", "location", "exercise", 
        and "count".

        The columns "date", "location", and "exercise" may 
        include empty entries; these are automatically
        forward-filled.

        The columns "time" and "count" must be entirely
        nonempty.
    """

    # obtain sheet name
    monthname = calendar.month_name[month]
    sheetname = "{}-{}".format(year, monthname)

    # import data
    df = import_exercise_sheet(filepath, sheetname)

    # check that the months and years in the data line up with the requested values
    for col in ['date', 'time']:
        vals = df[col].dt.year.unique()
        if (len(vals) > 1) or (vals[0] != year):
            raise ValueError("{} column contains dates outside desired year")
    
    for col in ['date', 'time']:
        vals = df[col].dt.month.unique()
        if (len(vals) > 1) or (vals[0] != month):
            raise ValueError("{} column contains dates outside desired month")
        
    return df








######################
# TOOLS FOR STATISTICS
######################



# Print standard stats for current month
#   Show monthly and daily total
#   Show per-day rep goals for a specified total monthly rep goal
def exercise_projection(filepath, exercise, goal_total):
    """Print statistics for a chosen exercise for the current month.
    
    The exercise records must be in an appropriately-formatted
        Apple Numbers file.

    
    Parameters
    ----------
    filepath : string
        The path to the Apple Numbers file containing the exercise
        records.

    exercise : string
        The name of the exercise to analyze.

    goal_total : int
        The goal for the total number of reps of the exercise to perform
        in the current month.
    
       
    Returns
    -------
    None

        
    Notes
    -----
        The data must be contained in a sheet titled "YYYY-MMMM", e.g. 
        "2024-November" to analyze the month of November 2024.

        The sheet must contain a single table (the name of the table 
        doesn't matter). That table's columns must be "date", "time", 
        "location", "exercise", and "count".

        The columns "date", "location", and "exercise" may include empty
        entries; these are automatically forward-filled.

        The columns "time" and "count" must be entirely nonempty.
    """

    ###################
    # IMPORT AND FILTER
    ###################

    # import this month's data
    year = date.today().year
    month = date.today().month
    day = date.today().day

    df = import_month(filepath, year, month)

    # check that the requested exercise appears in this month's data
    if exercise not in df["exercise"].unique():
        raise ValueError('Exercise "{}" not found in "exercise" column'.format(exercise))
    
    # filter to only the rows corresponding to the requested exercise
    df_subset = df[
        df["exercise"] == exercise
    ]

    ##############
    # PRINT HEADER
    ##############
    header = '{} FOR {}/{} AS OF {}/{}/{}'.format(
        exercise.upper(),
        month, year,
        day, month, year
    )
    print(header)
    print('-' * len(header))

    ##########################
    # MONTHLY AND DAILY TOTALS
    ##########################

    # total number done so far this month
    sum_month = df_subset['count'].sum()

    # total number done so far today
    sum_day = df_subset[
        df_subset['date'].dt.day == day
    ]['count'].sum()

    # print
    print("So far today: {}".format(sum_day))
    print("So far this month: {}".format(sum_month))

    #########################################
    # PER DAY GOALS FOR THE REST OF THE MONTH
    #########################################

    days_in_month = calendar.monthrange(year, month)[1]

    # reps per day for the rest of the month...
    #   ... as of this morning (no reps today):
    reps_per_day_morning = (
        goal_total - (sum_month - sum_day)
    ) / (days_in_month - (day - 1))
    #   ... at end of day (no more reps today):
    reps_per_day_eod = (
        goal_total - sum_month
    ) / (days_in_month - day)

    # print
    print("To reach {} by {}/{}:".format(goal_total, month, days_in_month))
    print("   As of this morning: {} per day".format(
        round(reps_per_day_morning, 2)
    ))
    print("   As of now: {} per day".format(
        round(reps_per_day_eod, 2)
    ))

    return None




# write function to analyze a previous month
#   total done in that month
#   number of days where I did something : total days in month
#   max reps in day
#   average reps per day (including and not including void days)
#   max reps in a set
#   average reps per set

def exercise_statistics(filepath, exercise, year = date.today().year, month = date.today().month):
    """Display statistics about a specified exercise for a specified month.
    
    The exercise records must be in an appropriately-formatted
        Apple Numbers file.

    
    Parameters
    ----------
    filepath : str
        The path to the Apple Numbers file containing the exercise
        records.

    exercise : string
        The name of the exercise to analyze.

    year, month : int
        The year and month for which to analyze the specified exercise.

        Default values: current year and month.
    

    Returns
    -------
    None

        
    Notes
    -----
        The data must be contained in a sheet titled "YYYY-MMMM", e.g. 
        "2024-November" to analyze the month of November 2024.

        The sheet must contain a single table (the name of the table 
        doesn't matter). That table's columns must be "date", "time", 
        "location", "exercise", and "count".

        The columns "date", "location", and "exercise" may include empty
        entries; these are automatically forward-filled.

        The columns "time" and "count" must be entirely nonempty.
    """

    if (year == date.today().year) and (month == date.today().month):
        day_range = date.today().day
        header = '{} FOR {}/{} AS OF {}/{}/{}'.format(
            exercise.upper(),
            month, year,
            day_range, month, year
        )
    else:
        day_range = calendar.monthrange(year, month)[1]
        header = '{} FOR {}/{}'.format(exercise.upper(), month, year)

    df = import_month(filepath, year, month)

    # check that the requested exercise appears in this month's data
    if exercise not in df["exercise"].unique():
        raise ValueError('Exercise "{}" not found in "exercise" column'.format(exercise))
    
    # filter to only the rows corresponding to the requested exercise
    df_subset = df[
        df["exercise"] == exercise
    ]

    print(header)
    header_len = len(header)
    print('-'*header_len)

    # total done in month

    total = df_subset['count'].sum()

    print('Total: {}'.format(total))

    # number of days where I did the exercise : total days in month

    days_done = len(df_subset['date'].dt.day.unique())

    print('Days done: {} of {}'.format(days_done, day_range))

    # max, avg reps in a set

    print('Per set:')

    max_reps_in_set = df_subset['count'].max()

    mean_reps_in_set = df_subset['count'].mean()

    median_reps_in_set = df_subset['count'].median()

    print('   max: {}'.format(max_reps_in_set))

    print('   mean: {}'.format(round(mean_reps_in_set, 2)))

    print('   median: {}'.format(median_reps_in_set))

    ########################
    # max, avg reps in a day
    ########################

    print('Per day:')
    
    # group by day and sum
    day_totals = df_subset.groupby('date')['count'].sum()

    # fill in void days
    day_totals_inc = pd.Series(
        index = [
            pd.Timestamp(year, month, day) for day in range(1, day_range+1)
        ]
    )

    for day in day_totals_inc.index:
        try:
            day_totals_inc[day] = day_totals[day]
        except:
            day_totals_inc[day] = 0

    
    max_reps_in_day = day_totals.max()

    mean_reps_in_day = day_totals.mean()
    mean_reps_in_day_inc = day_totals_inc.mean()

    median_reps_in_day = day_totals.median()
    median_reps_in_day_inc = day_totals_inc.median()

    print('   max: {}'.format(max_reps_in_day))
    print('   mean: {}'.format(round(mean_reps_in_day,2)))
    print('   median: {}'.format(median_reps_in_day))
    print('   mean, inc: {}'.format(round(mean_reps_in_day_inc, 2)))
    print('   median, inc: {}'.format(median_reps_in_day_inc))


    return None









#########################
# TOOLS FOR VISUALIZATION
#########################


# Transform exercise records into a list of DataFrames:
#   Each df contains precisely one set for each day,
#      and the nth df contains the nth set done on each day.
#   If I did fewer than n sets on a given day, that day's
#      entry contains a zero.

def stratify_exercise_month(
        df, exercise, date_format = "%Y-%m-%d"
):
    """Stratify the records for the specified exercise in the given data.

    Parameters
    ----------
    df : pandas.DataFrame
        The data containing the exercise records of interest.

        This DataFrame must be appropriately formatted (see "Notes").

    exercise : string
        The name of the exercise to stratify.

    date_format : string, default "%Y-%m-%d"
        The date format to use for the "date" columns in the
        output (see "Returns").

    
    Returns
    -------
    df_list : list of pandas.DataFrame
        Each DataFrame in df_list has columns "date" and "count"
        and precisely one row for each day in the month to which
        the given DataFrame df pertains.

        The DataFrame df_list[n-1] contains the nth set of the
        specified exercise for each day.

        If fewer than n sets were done on a given day, then that
        day's entry in df_list[n-1] contains a zero.

        
    Notes
    -----
        The given DataFrame's columns must be "date", "time", 
        "location", "exercise", and "count". 
        
        The "date" column must contain only dates for a single month.

        The columns "date", "location", and "exercise" may include 
        empty entries; these are automatically forward-filled.

        The columns "time" and "count" must be entirely nonempty.

        The output of import_month() can be safely used for the given
        DataFrame.
    """

    # check for appropriate data format
    df = clean_exercise_sheet(df)

    # check that the given DataFrame contains only records
    #   for a single year and month
    years_contained = df['date'].dt.year.unique()
    months_contained = df['date'].dt.month.unique()
    if (len(months_contained) != 1) or (len(years_contained) != 1):
        raise ValueError('Given DataFrame contains records for more than one month')
    
    # get the year and month value in the data
    month = months_contained[0]
    year = years_contained[0]

    # check that specified exercise appears in the given data
    if exercise not in df['exercise'].unique():
        raise ValueError('Exercise "{}" does not appear in "exercise" column'.format(exercise))

    # filter to specified exercise
    df_filtered = df[
        df['exercise'] == exercise
    ]

    #############################
    # Group by day, store as dict
    #############################

    # group by day
    grouped_by_date = df_filtered.groupby('date')

    # empty dict:
    #   Will contain each day of the month as keys,
    #      the sets performed that day as values.
    #   If I didn't do the specified exercise on a given day,
    #      then that day does not appear as a key.
    per_day_dict = {}

    for day, data in grouped_by_date:
        per_day_dict[day.strftime(date_format)] = data
        # the keys are strings formatted by date_format,
        #   not the actual datetime objects

    # sort each day's data by reps per set in descending order
    for key, val in per_day_dict.items():
        per_day_dict[key] = val.sort_values(
            by='count', ascending=False
        ).reset_index(drop=True)

    ##########
    # Stratify
    ##########

    # max number of sets done in a day:
    #   will be the length of the final list
    sets_per_day = [len(df) for df in per_day_dict.values()]

    n_sets_max = max(sets_per_day)

    # get day range
    #   if current month: current day
    #   if other month: number of days in the month
    if (month == date.today().month) and (year == date.today().year):
        day_range = date.today().day
    else:
        day_range = calendar.monthrange(year, month)[1]

    # list to contain the frames
    nth_set_list = []
    
    # for each set number...
    for n in range(n_sets_max):
        # ... initialize an empty dataframe:
        df = pd.DataFrame()
        # ... loop over every day in the month:
        for day in range(1, day_range+1):
            # obtain properly-formatted key for dict
            date_key = date(year, month, day).strftime(date_format)
            try:
                # pick out the nth set done on that day, if it happened
                rep = per_day_dict[date_key].loc[[n]][['date', 'count']]
                # NB .loc[[n]]: ensures that I get a 1-row dataframe, instead
                #   of a series
                # important so that the concatenation below works out right
            except:
                # if I didn't do n sets that day, fill in a set of zero reps
                rep = pd.DataFrame(
                    [
                        {'date': date_key, 'count': 0}
                    ]
                )
            # add set to the dataframe
            df = pd.concat([df, rep], axis=0)

        # reset index on completed dataframe
        df = df.reset_index(drop=True)
        # parse data column as dates
        df['date'] = pd.to_datetime(df['date'])
        # append to list
        nth_set_list.append(df)

    # return list of dataframes
    return nth_set_list



# Return stacked bar chart for a given month and exercise
def stacked_bar_exercise_month(filepath, exercise, year = date.today().year, month = date.today().month):
    """Produce a stacked bar chart for the given exercise for the given month.

    The exercise records must be in an appropriately-formatted
        Apple Numbers file.

    Parameters
    ----------
    filepath : str
        The path to the Apple Numbers file containing the exercise
        records.

    exercise : string
        The name of the exercise to plot.

    year, month : int
        The year and month for which to produce the bar chart.

        Default values: current year and month.

        
    Returns
    -------
    fig, ax
        The Matplotlib figure and axes objects containing the stacked
        bar chart.
    
    
    Notes
    -----
        The data must be contained in a sheet titled "YYYY-MMMM", e.g. 
        "2024-November" to analyze the month of November 2024.

        The sheet must contain a single table (the name of the table 
        doesn't matter). That table's columns must be "date", "time", 
        "location", "exercise", and "count".

        The columns "date", "location", and "exercise" may include empty
        entries; these are automatically forward-filled.

        The columns "time" and "count" must be entirely nonempty.
    """

    df = import_month(filepath, year=year, month=month)

    # stratify the given records
    nth_set_list = stratify_exercise_month(df, exercise)

    # obtain the necessary day range
    #   obtain from dataframes: gives length of month if non-current month,
    #   or gives current day if current month
    days_in_df = {len(df) for df in nth_set_list}

    # nth_set_list should contain dataframes of all the same length
    if len(days_in_df) != 1:
        raise ValueError('StratifyExerciseMonthBySet yields dataframes of nonuniform length')
    
    # obtain that single length
    day_range = days_in_df.pop()

    ################
    # MAKE THE PLOTS
    ################
    fig, ax = plt.subplots()

    # array to which to iteratively add each dataframe:
    #   produces stacking effect
    bottoms = np.zeros(day_range)
    
    for df in nth_set_list:
        # plot the set
        ax.bar(
            df['date'], df['count'],
            bottom = bottoms
        )
        # raise the bottoms of the next set to be plotted
        #   to the top of the set that was just plotted
        bottoms += df['count']

    # rotate the date labels for readability
    ax.set_xticks(ax.get_xticks(), ax.get_xticklabels(), rotation=90)

    # set title
    monthname = calendar.month_name[month]
    title = '{} per day for {} {}'.format(exercise.capitalize(), monthname, year)
    fig.suptitle(title, y=0.93)

    # return the figure and axes objects
    return fig, ax

    




# write function to produce overlaid line graphs for cumulative totals for each day or month
def cumsum_exercise_plot(filepath, exercise, **kwargs):
    """Plot cumulative totals for a specified exercise for the specified month(s).

    The exercise records must be in an appropriately-formatted
        Apple Numbers file.

        
    Parameters
    ----------
    filepath : str
        The path to the Apple Numbers file containing the exercise
        records.

    exercise : str
        The name of the exercise to analyze.

        
    Additional parameters
    ---------------------
    month : (int, int)
        The year (first element) and month (second element) for which
        to plot the exercise.

        Produces a single line plot.

        Cannot be used at the same time as startmonth and endmonth.

    startmonth, endmonth : (int, int)
        The year(s) (first element) and months (second element) for
        which to plot the exercise.

        Produces overlaid line plots.

        Cannot be used at the same time as month.

    
    Returns
    -------
    fig, ax
        The Matplotlib figure and axes objects containing the line
        plot(s).

    Notes
    -----
        The data must be contained in a sheet titled "YYYY-MMMM", e.g. 
        "2024-November" to analyze the month of November 2024.

        The sheet must contain a single table (the name of the table 
        doesn't matter). That table's columns must be "date", "time", 
        "location", "exercise", and "count".

        The columns "date", "location", and "exercise" may include empty
        entries; these are automatically forward-filled.

        The columns "time" and "count" must be entirely nonempty.
    """

    # making sure that either month is specified, or both startmonth and endmonth,
    #   but not both
    if ("month" in kwargs.keys()) and (
        ("startmonth" in kwargs.keys()) or ("endmonth" in kwargs.keys())
    ):
            raise ValueError(
                "month cannot be used alongside startmonth and endmonth"
            )
    
    if ("month" not in kwargs.keys()) and (
        ("startmonth" not in kwargs.keys()) or ("endmonth" not in kwargs.keys())
    ):
        raise ValueError(
            "Must specify either month, or startmonth and endmonth"
        )
        
    #######################
    # get lists of month(s), formatted as e.g. "2024-10"
    #######################
    if "month" in kwargs.keys():
        year = kwargs['month'][0]
        month = kwargs['month'][1]

        # list containing the single month
        monthlist = ["{}-{}".format(year, month)]

        

    if "startmonth" in kwargs.keys():
        # get start and end year and month
        startyear = kwargs['startmonth'][0]
        startmonth = kwargs['startmonth'][1]
        endyear = kwargs['endmonth'][0]
        endmonth = kwargs['endmonth'][1]

        # get full dates, for pandas use
        startdate = '{}-{}-01'.format(startyear, startmonth)
        enddate = '{}-{}-01'.format(endyear, endmonth)

        # list containing all sheetnames in specified range
        monthlist = [
            i.strftime("%Y-%m") for i in pd.date_range(
                start=startdate, end=enddate, freq="MS"
            )
        ]

    ###########
    # MAKE PLOT
    ###########
    fig, ax = plt.subplots()

    for year_month in monthlist:
        # split e.g. "2024-10" on hyphen
        split_month = year_month.split('-')
        year = int(split_month[0])
        month = int(split_month[1])

        # import data for e.g. "2024-10"
        df = import_month(filepath, year=year, month=month)
        
        # filter for specified exercise
        df_filtered = df[df['exercise'] == exercise]

        # get totals for each day, then cumulative sum
        #   to get running total
        cumulative = df_filtered.groupby('date')['count'].sum().cumsum()

        # get isolated "day" column
        cumulative = cumulative.reset_index()

        cumulative['day'] = cumulative['date'].dt.day

        # make line plot
        ax.plot(
            cumulative['day'], cumulative['count'], marker=".",
            label=year_month
        )

    # rotate x-axis labels
    ax.set_xticks(
        ax.get_xticks(),
        ax.get_xticklabels(),
        rotation=90
    )

    # make legend
    ax.legend()

    # make title
    if 'month' in kwargs.keys():
        monthname = calendar.month_name[month]
        title = '{} for {} {}'.format(exercise.capitalize(), monthname, year)

    if 'startmonth' in kwargs.keys():
        title = '{} (cum. total) for {}-{} through {}-{}'.format(
            exercise.capitalize(), startyear, startmonth, endyear, endmonth
        )

    fig.suptitle(title, y=0.93)




    return fig, ax




    

    
    














# write function to produce bar chart: number of sets done with each number of reps