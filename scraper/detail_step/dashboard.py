try:
    import scraper.tool.utils as utl
except ImportError:
    import tool.utils as utl

import matplotlib.pyplot as plt
import seaborn as sns


# -----------------------------------------------------------------------------------


def util_num_rating_star(axes, df):
    try:
        df = df[['Name', 'Utility_num', 'Rating_star']].copy()
        # print(df)

        sns.regplot(data=df, x='Utility_num', y='Rating_star', ax=axes)
        axes.set_title('Utility_num vs Rating_star')
        axes.grid(True, linestyle='--', alpha=0.8) 

    except Exception as e:
        utl.log_error(e)



def rating_category_ratio(axes, df):
    try:
        df = df.copy()
        df_visible = df[df['Counts'] > 0]
        # print(df_visible)

        wedges = axes.pie(x=df_visible['Counts'], autopct='%1.1f%%', colors=sns.color_palette('pastel', n_colors=len(df_visible)))[0]
        
        axes.set_title('Rating ratio')
        axes.legend(handles=wedges, labels=df_visible['Rating_Category'].to_list(), title='Rating', loc='best')
        axes.axis('equal') # Ensure pie chart is circular

    except Exception as e:
        utl.log_error(e)




def rating_num_rating_star(axes, df):
    try:
        df = df[['Name', 'Rating_num', 'Rating_star']].copy()
        # print(df)

        sns.regplot(data=df, x='Rating_num', y='Rating_star', ax=axes)
        axes.set_title('Rating_num vs Rating_star')
        axes.grid(True, linestyle='--', alpha=0.8) 

    except Exception as e:
        utl.log_error(e)



def this_month_BR_rating_star(axes, df):
    try:
        df = df[['Name', 'This_month_booked_rate', 'Rating_star']].copy()
        # print(df)

        sns.regplot(data=df, x='Rating_star', y='This_month_booked_rate', ax=axes)
        axes.set_title('This_month_booked_rate vs Rating_star')
        axes.grid(True, linestyle='--', alpha=0.8) 

    except Exception as e:
        utl.log_error(e)



def next_1month_BR_rating_star(axes, df):
    try:
        df = df[['Name', 'Next_1_month_booked_rate', 'Rating_star']].copy()
        # print(df)

        sns.regplot(data=df, x='Rating_star', y='Next_1_month_booked_rate', ax=axes)
        axes.set_title('Next_1_month_booked_rate vs Rating_star')
        axes.grid(True, linestyle='--', alpha=0.8) 

    except Exception as e:
        utl.log_error(e)



def next_3month_BR_rating_star(axes, df):
    try:
        df = df[['Name', 'Next_3_month_booked_rate', 'Rating_star']].copy()
        # print(df)

        sns.regplot(data=df, x='Rating_star', y='Next_3_month_booked_rate', ax=axes)
        axes.set_title('Next_3_month_booked_rate vs Rating_star')
        axes.grid(True, linestyle='--', alpha=0.8) 

    except Exception as e:
        utl.log_error(e)