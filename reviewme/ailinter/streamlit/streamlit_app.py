import sys
import pandas as pd
import streamlit as st

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


########################
## STREAMLIT CONFIG
########################

st.set_page_config(
    page_title="AI Feedback Viewer",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="collapsed", 
)
# st.title("💚 AI Feedback Viewer 💚")
st.markdown("<h1 style='text-align: center;'>💚 AI Feedback Viewer 💚</h1>", unsafe_allow_html=True)

################################
## DATAFRAME FILTER 
################################
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df

################################
## DISPLAY HELPERS 
################################

st.cache_data()
def load_data(file_path):
    return pd.read_csv(file_path)

def display_dataframe(df):
    # Replace newline characters with HTML line breaks
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('\n', '<br>')

    # Define CSS to control column widths
    
    css = """
    <style>
    table.dataframe td {
        vertical-align: top;
        font-size: 18px; 
    }
    table.dataframe th {
        text-align: center;
    }

    </style>
    """

    ### Table Mode 
    # Apply CSS and display DataFrame
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    ### DataFrame Mode
    # Apply CSS and display DataFrame
    # st.markdown(css, unsafe_allow_html=True)
    # st.dataframe(df, use_container_width=True)  # Use st.dataframe for now instead of st.markdown to make it sortable
    # st.dataframe(filter_dataframe(df))
    

################################
## MAIN
################################
# sys.argv[1] will contain the file path, as passed in from the os.system call from ailinter.py:run()
csv_file_path = sys.argv[1]
# print ("csv_file_path: ", csv_file_path)
df = load_data(csv_file_path)

# check if df is empty 
if df.empty or df is None:
    st.write("No feedback items to display")
else: 
    # Display the DataFrame
    display_dataframe(df)


################################
## WIP FUTURE WORK 
################################

# st.cache_data()
# def load_data(file_path):
#     return pd.read_csv(file_path)

# st.cache_data()
# def display_dataframe(df):
#     # Replace newline characters with HTML line breaks
#     for col in df.columns:
#         if df[col].dtype == 'object':
#             df[col] = df[col].str.replace('\n', '<br>')

#     # Display function name in backticks
#     if 'Function Name' in df.columns:
#         df['Function Name'] = df['Function Name'].apply(lambda x: f'`{x}`')

#     # Iterate over DataFrame rows
#     for index, row in df.iterrows():
#         # Create a Streamlit component for each row
#         st.markdown(f"**Function Name:** {row['Function Name']}")
#         st.markdown(f"**Error Category:** {row['Error Category']}")
#         st.markdown(f"**Fail:** {row['Fail']}")
#         st.markdown(f"**Fix:** {row['Fix']}")
#         st.button("Explain this issue")
#         st.button("See fix")
#         st.write("---")  # Add a horizontal line for visual separation

## Markdown version 
# def display_dataframe(df):
#     # Replace newline characters with HTML line breaks
#     for col in df.columns:
#         if df[col].dtype == 'object':
#             df[col] = df[col].str.replace('\n', '<br>')

#     # Define CSS to control column widths
#     css = """
#     <style>
#     table.dataframe td {
#         vertical-align: top;
#         font-size: 18px; 
#     }
#     table.dataframe th {
#         text-align: center;
#     }
#     </style>
#     """

#     # Apply CSS and display DataFrame
#     st.markdown(css, unsafe_allow_html=True)
#     st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)