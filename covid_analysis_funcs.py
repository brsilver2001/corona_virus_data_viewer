import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

def do_exponential_curve_fit(x_values, y_values):
    y_logs = list(np.log(y_values))
    try:
        c =  np.polyfit(x_values, y_logs,1)
    except:
        c = [0, 0]
    return c

def get_exponential_curve_function(x_values, y_values):
    """Return a lambda function that represents the curve fit in log space"""
    c = do_exponential_curve_fit(x_values, y_values)
    return lambda x:np.exp(c[0]*x + c[1])

def date_as_float(dt):
    """returns datetime as number of days since base date"""
    base_date = datetime.datetime(2020,2,1)
    return (dt-base_date).total_seconds()/(60*60*24)

def float_to_date(days):
    base_date = datetime.datetime(2020,2,1)
    return base_date + datetime.timedelta(days=days)

def find_exponential_fit(x_values, y_values, start_x=None, end_x=None):
    base_date = datetime.datetime(2020,2,1)
    x_val = list(x_values.copy())
    use_dates = isinstance(x_val[0], (datetime.datetime, np.datetime64))

    if use_dates:
        x_val = [date_as_float(dt) for dt in x_val]

    x_used = []
    y_used = []
    for x, y in zip(x_val, y_values):
        if y > 0:
            x_used.append(x)
            y_used.append(y)

    curve_function = get_exponential_curve_function(x_used, y_used)

    if start_x is None:
        start_x = min(x_used)
    if end_x is None:
        end_x = max(x_used)
    if isinstance(start_x, (datetime.datetime, np.datetime64)):
        start_x = date_as_float(start_x)
    if isinstance(end_x, (datetime.datetime, np.datetime64)):
        end_x = date_as_float(end_x)

    return_x = np.linspace(start_x, end_x, 30)
    return_y = [curve_function(x) for x in return_x]
    if use_dates:
        return_x = [float_to_date(x) for x in return_x]

    return (return_x, return_y)

def plot_one_trace(df_input, ax, first_date, latest_date, markersize=20, label=""):
    df = df_input.copy()
    df = df[(df.Datetimes >= first_date) &
             (df.Datetimes <= latest_date)]

    confirmed_fit = find_exponential_fit(df.Datetimes, df.Confirmed,
                                        start_x = first_date,
                                        end_x = latest_date)

    ax[0,0].scatter(df.Datetimes,df.Confirmed, s=markersize, label=label)
    ax[0,0].plot(confirmed_fit[0], confirmed_fit[1], label="curve fit")
    ax[0,0].set_title("Confirmed by date")

    deaths_fit = find_exponential_fit(df.Datetimes, df.Deaths,
                                        start_x = first_date,
                                        end_x = latest_date)

    ax[1,0].scatter(df.Datetimes, df.Deaths, s=markersize, label=label)
    ax[1,0].plot(deaths_fit[0], deaths_fit[1], label="curve fit")
    ax[1,0].set_title("Deaths by date")

    ax[2,0].scatter(df.Datetimes, df.Recovered, s=markersize, label=label)
    ax[2,0].set_title("Recovered by date")

    ax[0,1].scatter(df.Datetimes,df.Confirmed, s=markersize, label=label)
    ax[0,1].plot(confirmed_fit[0], confirmed_fit[1], label="curve fit")
    ax[0,1].set_yscale('log')
    ax[0,1].set_title("Confirmed by date  -- log scale")

    ax[1,1].scatter(df.Datetimes, df.Deaths, s=markersize, label=label)
    ax[1,1].plot(deaths_fit[0], deaths_fit[1], label="curve fit")
    ax[1,1].set_yscale('log')
    ax[1,1].set_title("Deaths by date  -- log scale")

    ax[2,1].scatter(df.Datetimes, df.Recovered, s=markersize, label=label)
    ax[2,1].set_yscale('log')
    ax[2,1].set_title("Recovered by date  -- log scale")

def format_axis(first_date, latest_date, ax):
    dt = ((latest_date - first_date) / 4)
    x_tick_list = [first_date + i* dt for i in range(4)] + [latest_date]

    for axis_row in ax:
        for axis in axis_row:
            axis.set_xlim([first_date, latest_date])
            axis.set_xticks(x_tick_list)
            axis.legend(loc=2)

def plotstuff(df_input, first_date=None, latest_date=None, label=""):
    df = df_input.copy()
    df.sort_values('Datetimes', inplace=True)
    if first_date is None:
        first_date = datetime.datetime(2020,1,20)
    if latest_date is None:
        latest_date = max(df.Datetimes) + datetime.timedelta(days=3)

    fig, ax = plt.subplots(3,2, figsize=(14,14))
    plot_one_trace(df, ax, first_date=first_date, latest_date=latest_date,
                   markersize=30, label=label)
    format_axis(first_date, latest_date, ax)


def get_row_data(df, this_date):
    this_row = df[df.Datetimes == this_date]
    this_confirmed=this_row.Confirmed.values[0]
    this_deaths=this_row.Deaths.values[0]
    this_recovered=this_row.Recovered.values[0]
    return int(this_confirmed), int(this_deaths), int(this_recovered)

def stats_last_7_days(df, this_date, day_count=7):
    last_7_days_data = df[df.Datetimes >= this_date - datetime.timedelta(days=day_count)]
    times = list(last_7_days_data.Datetimes)
    times = [date_as_float(time) for time in times]
    confirmed = list(last_7_days_data.Confirmed)
    deaths = list(last_7_days_data.Deaths)


    if confirmed[0] > 0:
        confirmed_multiplier_increase = confirmed[-1]/confirmed[0]
    else:
        confirmed_multiplier_increase = 0
    c = do_exponential_curve_fit(times, confirmed)

    confirmed_daily_increase_pct = (np.exp(c[0])-1)*100
    confirmed_doubling_rate = 72/confirmed_daily_increase_pct

    if deaths[0] > 0:
        deaths_multiplier_increase = deaths[-1]/deaths[0]
    else:
        deaths_multiplier_increase = 0

    c = do_exponential_curve_fit(times, deaths)

    deaths_daily_increase_pct = (np.exp(c[0])-1)*100
    deaths_doubling_rate = 72/deaths_daily_increase_pct

    return (confirmed_multiplier_increase, confirmed_daily_increase_pct, confirmed_doubling_rate,
            deaths_multiplier_increase, deaths_daily_increase_pct, deaths_doubling_rate)

def printstuff(df,latest_date=None, day_count=7):
    if latest_date is None:
        latest_date = max(df.Datetimes)
    print(f"Rates based on last {day_count} days")

    print("Confirmed                      Dead")
    print(2*" multi-  daily      days to    ")
    print(2*" plier   increase   double     ")
    last_week = stats_last_7_days(df, latest_date, day_count)
    print(f"  {last_week[0]:4.1f}x  {last_week[1]:4.1f}%     {last_week[2]:4.1f}       ",
          f"  {last_week[3]:4.1f}x  {last_week[4]:4.1f}%     {last_week[5]:4.1f}")


    print("Week summary")
    print("                Confirmed           Death       Recovered")
    print("date         total  today    total  today    total  today")

    for rows in range(-7, 1):
        this_date = latest_date + datetime.timedelta(days=rows)
        previous_date = latest_date + datetime.timedelta(days=rows-1)

        (this_confirmed, this_deaths,
         this_recovered) = get_row_data(df, this_date)

        (previous_confirmed, previous_deaths,
         previous_recovered) = get_row_data(df,previous_date)

        print(f"{this_date.strftime('%m/%d/%Y'):9}",
              f"{this_confirmed:8} {this_confirmed - previous_confirmed:6}",
              f"{this_deaths:8} {this_deaths - previous_deaths:6}",
              f"{this_recovered:8} {this_recovered - previous_recovered:6}")
