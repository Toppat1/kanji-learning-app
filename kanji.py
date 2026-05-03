import streamlit as st
import pandas as pd
import requests

# Set page layout (centered or use whole screen with 'wide')
st.set_page_config(
    page_title="Kanji Learning App",
    layout="centered"
)

# Set title heading
st.title("Kanji App!")
st.header("By Firas")

# Create a function to break down a Japanese sentence into individual pieces
def breakdown_sentence(sentence: str):

    # Specify JPDB.io API parameters
    url = "https://jpdb.io/api/v1/parse"

    # API input and outputs
    payload = {
    "text": sentence,
    "token_fields": ["vocabulary_index", "position", "length", "furigana"],
    "position_length_encoding": "utf32",
    "vocabulary_fields": ["spelling", "reading", "meanings"]
    }

    # Authorisation info
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {st.secrets['JPDB_API_KEY']}"
    }

    # Call the JPDB API to break down the JP sentence
    response = requests.post(url, json=payload, headers=headers).json()

    # Split output dictionary into Tokens and Vocabulary
    tokens = response['tokens']
    vocabulary = response['vocabulary']

    # Initialise an empty dataframe
    df = pd.DataFrame()

    # Clean data to put into dataframe columns
    for index, token in enumerate(tokens):
    
        df.loc[index, 'vocabulary_index'] = token[0]
        df.loc[index, 'sentence_position'] = token[1]
        df.loc[index, 'length'] = token[2]

        df.loc[index, 'section'] = sentence[token[1]: token[1] + token[2]]

        if token[3] == None:
            df.loc[index, 'base_kanji'] = None
            df.loc[index, 'base_kanji_hiragana'] = None
            df.loc[index, 'connector'] = None
            df.loc[index, 'ending'] = None
        else:
            print(token[3])

            df.loc[index, 'base_kanji'] = token[3][0][0]
            df.loc[index, 'base_kanji_hiragana'] = token[3][0][1]

            if len(token[3]) == 1:
                df.loc[index, 'connector'] = None
                df.loc[index, 'ending'] = None
            
            elif len(token[3]) > 2:
                df.loc[index, 'connector'] = token[3][1]
                df.loc[index, 'ending'] = token[3][-1]
            else:
                df.loc[index, 'connector'] = None
                df.loc[index, 'ending'] = token[3][1] 

    # Vocabulary part cleaning
    for index, vocab in enumerate(vocabulary):
        df.loc[index, 'base_word'] = vocab[0]
        df.loc[index, 'base_word_hiragana'] = vocab[1]

        # To prevent errors, create a meanings column and cells before assigning a list to it
        df.loc[index, 'base_word_meanings'] = None
        df.at[index, 'base_word_meanings'] = vocab[2]

    # Return the dataframe and raw API output
    return [df, response]

# Section heading
st.subheader("Sentence Input")

# Create a user input
st.text_input(
    label="Enter a Japanese sentence to break down...", 
    placeholder="リンゴを早く食べましたので、嬉しかった。",
    value="リンゴを早く食べましたので、嬉しかった。",
    key='sentence'
)

# Create a loading spinner while table loads
with st.spinner('Loading...', show_time=True):

    # Create dataframe using inputted sentence broken down
    df = (
        breakdown_sentence(st.session_state.sentence)[0]
        .rename(
            columns = {
                'vocabulary_index':'Vocabulary Index',
                'sentence_position':'Sentence Position Index',
                'length':'Length',
                'section':'Component',
                'base_kanji':'Kanji',
                'base_kanji_hiragana':'Kanji (Hiragana)',
                'connector':'Connector',
                'ending':'Ending',
                'base_word':'Base Word',
                'base_word_hiragana':'Base Word (Hiragana)',
                'base_word_meanings': 'Base Definitions'
            }
        )      
    )

    # Style the dataframe with coloured columns!
    styled_df = (
        df[['Component', 'Kanji', 'Kanji (Hiragana)', 'Connector', 'Ending']]   
        .style.set_properties(
            subset=['Component'],
            **{'background-color': "#fff3b0b2"}
        )

        .set_properties(
            subset=['Kanji (Hiragana)', 'Connector', 'Ending'],
            **{'background-color': "#c228b853"}
        )

    )

    # Table title
    st.subheader("Components")

    # Print the df/raw output of the API sentence breakdown
    st.dataframe(
        styled_df, 
        hide_index=True)
    
    # Table title
    st.subheader("Definitions")
    
    st.dataframe(
        df[['Base Word', 'Base Word (Hiragana)', 'Base Definitions']]
        .style.set_properties(
            subset=['Base Word', 'Base Word (Hiragana)'],
            **{'background-color': "#31f0ba99"}
        ), 
        hide_index=True)