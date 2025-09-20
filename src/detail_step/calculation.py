try:
    import app.tool.utils as utl
except ImportError:
    import tool.utils as utl

import pandas as pd


# -----------------------------------------------------------------------------------


def cnt_rating_categories(df):
    try:
        property_full_df = df[['Name', 'Rating_star']].copy()
        # print(property_full_df)

        bins = [1, 2, 3, 4, 5, 5.0001]
        labels = ['1-1.9', '2-2.9', '3-3.9', '4-4.9', '5']
        property_full_df['Rating_category'] = pd.cut(
            property_full_df['Rating_star'],
            bins=bins,
            labels=labels,
            include_lowest=True,
            right=False
        )

        # print('Categorized column created')
        # print(property_full_df)
        # print('-'*30)

        rating_cnt = property_full_df['Rating_category'].value_counts().sort_index()
        new_df = pd.DataFrame(rating_cnt).reset_index()
        new_df.columns = ['Rating_Category', 'Counts']

        # print('New categorized count df created')
        # print(new_df)
        # print('-'*30)

        return new_df

    except Exception as e:
        utl.log_error(e)