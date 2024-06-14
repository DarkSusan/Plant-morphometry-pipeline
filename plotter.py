import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from glob import glob

def load_data(file_path):
    with open(file_path) as f:
        data = json.load(f)

    observations = data.get('observations', {}).get('default_1', {})

    flat_data = {}
    for key, obs in observations.items():
        value = obs['value']
        if isinstance(value, list):
            flat_data[key] = value
        else:
            flat_data[key] = value
    return flat_data

file_paths = glob('results/*.json')
data_frames = {file_path: load_data(file_path) for file_path in file_paths}

def plot_histogram(trait):
    plt.figure(figsize=(10, 6))
    for file_path, data in data_frames.items():
        if trait in data and isinstance(data[trait], list):
            sns.histplot(data[trait], kde=False, label=file_path, bins=30)
    plt.title(f'Histogram of {trait}')
    plt.xlabel('Frequency')
    plt.ylabel('Count')
    plt.legend()
    st.pyplot(plt.gcf())

def plot_bar(trait):
    plt.figure(figsize=(10, 6))
    bar_data = {file_path: data[trait] for file_path, data in data_frames.items() if
                trait in data and not isinstance(data[trait], list)}
    bar_df = pd.DataFrame(list(bar_data.items()), columns=['File', trait])
    sns.barplot(data=bar_df, x='File', y=trait, palette='viridis')
    plt.title(f'Bar Plot of {trait}')
    plt.xlabel('File')
    plt.ylabel(trait)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt.gcf())


traits = list(data_frames[file_paths[0]].keys())

selected_trait = st.selectbox('Select Trait for Bar Plot', traits)
if selected_trait:
    plot_bar(selected_trait)

hist_trait = st.selectbox('Select Trait for Histogram', traits)
if hist_trait:
    plot_histogram(hist_trait)
