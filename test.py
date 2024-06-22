import pandas as pd
import streamlit as st
from io import StringIO

def load_and_clean_csv(file):
    content = file.getvalue().decode("utf-8")
    lines = content.splitlines()
    start_index = next(i for i, line in enumerate(lines) if line.startswith("First Name"))
    cleaned_content = "\n".join(lines[start_index:])
    df = pd.read_csv(StringIO(cleaned_content))
    return df

def filter_connections_by_company(df, company):
    filtered_df = df[df['Company'].str.contains(company, case=False, na=False)].reset_index(drop=True)
    filtered_df.index += 1
    return filtered_df[['First Name', 'Last Name', 'URL']]

def make_clickable(url):
    return f'<a href="{url}" target="_blank">{url}</a>'

def main():
    st.title("LinkedIn Connections Explorer")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        df = load_and_clean_csv(uploaded_file)
        st.write("CSV file successfully loaded and cleaned.")
        
        company = st.text_input("Enter the company you are interested in:")
        if company:
            filtered_df = filter_connections_by_company(df, company)
            if not filtered_df.empty:
                st.write(f"Connections working at {company} ({len(filtered_df)} connections):")
                filtered_df['URL'] = filtered_df['URL'].apply(make_clickable)
                st.write(filtered_df.to_html(escape=False, index=True), unsafe_allow_html=True)
            else:
                st.write(f"No connections found working at {company}.")
        
        st.write("## Column Filters")
        for column in df.columns:
            selected_values = st.multiselect(f"Filter {column}", df[column].unique())
            if selected_values:
                df = df[df[column].isin(selected_values)]
        
        st.write("## Filtered Data")
        if 'URL' in df.columns:
            df['URL'] = df['URL'].apply(make_clickable)
        st.write(df.to_html(escape=False, index=True), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
