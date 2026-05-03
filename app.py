import streamlit as st
import pandas as pd
import numpy as np
import time

# How do you display a title and normal text?
st.title("Hello World!")

st.write("This is a text")

# How do you display a Pandas dataframe?
df = pd.DataFrame({
    'player':['Toppat','sub neko', 'Konaii'],
    'kd':[2,1,1.5]
})

df

# How do you display a dataframe using st.write()?
st.write("i'm bout to pass in a dataframe to st.write")

st.write(pd.DataFrame({
    'poo':['white','brown'],
    'size':[1,10],
    'yum':['ew','delicious']
}))

# How do you display a static chart? A static chart doesn't have any interactive elements like scrolling or zooming in.
st.table(df)

# How do you display a dataframe with styling features?
dataframe = pd.DataFrame(
    np.random.randn(3,4),
    columns=('col %d' % num for num in range(4)) # For each column name, make it "col X" where X ranges from 0 to 4
)

st.dataframe(dataframe.style.highlight_max(axis='rows'))

# How do you display a line chart?
chart_data = pd.DataFrame(
    np.random.randn(20,3),
    columns=['a','b','c']
)

st.title('Line Chart of Random Normal Distribution Values', text_alignment='center', help='Title of Chart')

st.line_chart(chart_data, x_label='iteration', y_label='normal dist val')

# How do you display data points on a map?
map_data = pd.DataFrame(
    np.random.randn(1000,2) / [50, 50] + [37.76, -122.4],
    columns=['lat','lon']
)

st.map(map_data)

# What is a widget?
# An interactive plaything to add to your app!

# How do you create a slider?
x = st.slider('x')
st.write(x, 'squared is', x * x)

# How do you create a key (e.g. variable value from user input)?
st.text_input("Your Name", key="name")
st.session_state.name

st.write("Your name is ", st.session_state['name'])

# How do you create a checkbox?
if st.checkbox("Show DataFrame"):
    chart_data

# How do you create a select box, to choose from a list of options?
option = st.selectbox(
    'Who are you?',
    df['player']
)

'You selected:', option

# How do you add a selectbox and slider to a sidebar?

st.sidebar.title('Welcome, Firas!')

add_selectbox = st.sidebar.selectbox(
    'How would you like us to contact you?',
    ('Email', 'Home phone', 'Mobile phone')
)

add_slider = st.sidebar.slider(
    'Age',
    1.0, 100.0, (25.0,75.0),
    key='age',
    
)

# How do you access the value of a widget?
add_slider
add_selectbox
st.session_state.age

# How do you place widgets side-by-side?
left_column, right_column = st.columns(2)
left_column.button('Press me!')

# How do you select a column?
# How do you create a bullet list checkbox?
with right_column:
    chosen = st.radio(
        'Colour',
        ('Blue','Yellow','Green','Purple')
    )
    st.write(f"You chose the colour: {chosen}")

# How do you display the actual code you wrote to do something?
with st.echo():
    st.write('Look at this code I used to create this text!')

# How do you create a loading spinner?
with st.spinner('Wait for it...', show_time=True):
    time.sleep(1)

st.success('Done!')
st.button('Rerun!')

# When would you want to create a progress bar?
# When you have a computation that takes a long time

# How do you create a progress bar?
'Starting a long computation...'

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
    # Update the progress bar with each iteration.
    latest_iteration.text(f'Iteration {i+1}')
    bar.progress(i+1)
    time.sleep(0.01)

'... and now we\'re done!'

if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1

st.header(f'This page has been run {st.session_state.counter} times.')
st.button('Run it again!')