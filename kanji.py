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

# Authorisation info for JPDB API calls
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {st.secrets['JPDB_API_KEY']}"
}

# Break down a Japanese sentence into individual components
@st.cache_data
def breakdown_sentence(sentence: str):

    # Specify JPDB.io API parameters
    url = "https://jpdb.io/api/v1/parse"

    # API input and outputs
    payload = {
    "text": sentence,
    "token_fields": ["vocabulary_index", "position", "length", "furigana"],
    "position_length_encoding": "utf32",
    "vocabulary_fields": ["spelling", "reading", "meanings", "part_of_speech"]
    }

    # Call the JPDB API to break down the JP sentence
    response = requests.post(url, json=payload, headers=headers).json()

    # Split output dictionary into Tokens and Vocabulary
    tokens = response['tokens']
    vocabulary = response['vocabulary']

    # Initialise an empty dataframe
    df = pd.DataFrame()

    # Initialise empty columns + names
    df["section"] = None
    df["kanji"] = None
    df["kanji_hiragana"] = None
    df["connector"] = None
    df["ending"] = None
    df["base_word_meanings"] = None
    df["part_of_speech"] = None

    df["vocabulary_index"] = None
    df["sentence_position"] = None
    df["length"] = None

    # Clean data to put into dataframe columns
    for index, token in enumerate(tokens):
        # DEBUGGING STEP
        # st.write(tokens)
    
        # Set column cells with data that is always a single value, not a list
        df.loc[index, 'vocabulary_index'] = token[0]
        df.loc[index, 'sentence_position'] = token[1]
        df.loc[index, 'length'] = token[2]

        # Select the sentence component by using its position index and length
        df.loc[index, 'section'] = sentence[token[1]: token[1] + token[2]]

        # If the component has furigana, i.e. has kanji
        if token[3]:
            # DEBUGGING STEP
            # st.write("Currently working on:", token)

            # Initialise the empty lists for kanjis and hiragana versions of kanjis
            df.at[index, 'kanji'] = []
            df.at[index, 'kanji_hiragana'] = []

            # For each kanji list, append its kanji, hiragana version, connector (if exists), and endings of the word (conjugation)
            for element_index, element in enumerate(token[3]):

                if isinstance(element, list):
                    df.loc[index, 'kanji'].append(element[0])
                    df.loc[index, 'kanji_hiragana'].append(element[1])
                else:
                    if element_index == len(token[3]) - 1:
                        df.loc[index, 'ending'] = element
                    elif element_index == len(token[3]) - 2:
                        df.loc[index, 'connector'] = element  

    # Vocabulary part cleaning
    for index, vocab in enumerate(vocabulary):
        df.loc[index, 'base_word'] = vocab[0]
        df.loc[index, 'base_word_hiragana'] = vocab[1]

        # To prevent errors, create a meanings column and cells before assigning a list to it
        df.at[index, 'base_word_meanings'] = vocab[2]

        df.at[index, 'part_of_speech'] = vocab[3]

    # Return the dataframe and raw API output
    return df

# Fetch the machine translation of the Japanese sentence
@st.cache_data
def translate_jp(jp_sentence: str):
    return requests.post(url = "https://jpdb.io/api/v1/ja2en", json={"text":jp_sentence}, headers=headers).json()['text']

# Section heading
st.subheader("Input")

# Create a text box for the user to input a Japanese sentence
sentence = st.text_input(
    label="Enter a Japanese sentence to break down...", 
    placeholder="リンゴを早く食べましたので、嬉しかった。",
    value="リンゴを早く食べましたので、嬉しかった。",
    key="sentence"
)

# On first website run, set this to the current placeholder sentence
if "previous_sentence" not in st.session_state:
    st.session_state["previous_sentence"] = sentence

# Create df and a loading spinner while table loads
with st.spinner('Loading...', show_time=True):

    # Create dataframe using inputted sentence broken down
    df = (
        # Call the breakdown sentence function
        breakdown_sentence(sentence)
        .rename(
            columns = {
                'vocabulary_index':'Vocabulary Index',
                'sentence_position':'Sentence Position Index',
                'length':'Length',
                'section':'Component',
                'kanji':'Kanji',
                'kanji_hiragana':'Kanji (Hiragana)',
                'connector':'Connector',
                'ending':'Ending',
                'base_word':'Base Word',
                'base_word_hiragana':'Base Word (Hiragana)',
                'base_word_meanings': 'Base Definitions',
                'part_of_speech':'Part of Speech'
            }
        )      
    )
    translated_sentence = translate_jp(sentence)

    # Style the dataframe with coloured columns!
    styled_df = (
        df[['Component', 'Kanji', 'Kanji (Hiragana)', 'Connector', 'Ending', 'Part of Speech']]   
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

# Section heading
st.subheader("Translation")
st.text(f"{sentence}")

# Clear the attempted translation if the sentence was changed
if sentence != st.session_state["previous_sentence"]:
    st.session_state["attempted_translation"] = ""
    st.session_state["previous_sentence"] = sentence

# Allow the user to guess the meaning of their sentence from the breakdown
attempted_translation = st.text_input(
    label="What do you think this sentence is in English?",
    placeholder="Enter translation...",
    key="attempted_translation"
)

# Only reveal the translation button if the user tried to translate it themselves
if attempted_translation:
    if st.button(label="Reveal answer!"):
        st.write(translated_sentence)

sentence_db = pd.read_csv(r'sentence_data.csv')

cleaned_sentence_db = (
    sentence_db.groupby('jp')
    ['eng']
    .apply(list)
    .reset_index()
)

# st.dataframe(cleaned_sentence_db.sample(n=10), hide_index=True)

kanji_search = st.text_input(
    label='Sentence Searcher',
    placeholder='Enter kanji...'
)

st.dataframe(cleaned_sentence_db[cleaned_sentence_db['jp'].str.contains(kanji_search)], hide_index=True)