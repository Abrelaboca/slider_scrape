import os
import eyed3
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import json
import time

# Number of genre clusters to create.
num_clusters = 5

# Define the source directory where your songs are located.
source_directory = "songs"
bpm_data_file = "bpm_data.json"  # File to store BPM data

# Define the destination directories for different genres and their respective BPM ranges.
genre_directories = {
    "55-79": (55, 79),
    "80-97": (80, 97),
    "98-116": (98, 116),
    "breakbeat": (117, 151),                                                 
    "dnb": (160, 195)
}

# Function to create genre directories if they don't exist.
def create_genre_directories():
    for genre in genre_directories:
        genre_path = os.path.join(source_directory, genre)
        if not os.path.exists(genre_path):
            os.mkdir(genre_path)

# Function to get the BPM from a song file using eyed3.
def get_bpm(song_file):
    if not any(key in song_file for key in genre_directories.keys()):
        audiofile = eyed3.load(song_file)
        if audiofile.tag and audiofile.tag.bpm:
            return int(audiofile.tag.bpm)
        return None

# Function to move a song to the appropriate genre directory.
def move_song(song_name, source_path, genre):
    destination_path = os.path.join(source_directory, genre, song_name)
    try:
        os.rename(source_path, destination_path)
        print(f"Moved '{source_path}' to '{genre}'")
        time.sleep(0.1)
    except FileExistsError as fe:
        print(f"{source_path} exists in destination.")
    

# Function to visualize the clustering results.
def visualize_clusters(bpm_data, cluster_labels):
    plt.figure(figsize=(12, 6))

    # Create a scatter plot of BPM values colored by cluster labels.
    plt.subplot(1, 2, 1)
    plt.scatter(bpm_data, np.zeros_like(bpm_data), c=cluster_labels, cmap='viridis')
    plt.xlabel("BPM")
    plt.title("Cluster Plot")

    # Create a histogram of BPM values.
    plt.subplot(1, 2, 2)
    plt.hist(bpm_data, bins=50, edgecolor='k')
    plt.xlabel("BPM")
    plt.ylabel("Count")
    plt.title("BPM Histogram")

    plt.show()

# Function to analyze the BPM values and determine genre clusters.
def analyze_bpm_and_determine_genres():
    all_bpms = read_bpm_data()

    if not all_bpms:
        calculate_and_store_bpm_data()
        all_bpms = read_bpm_data()

    # Perform K-Means clustering to determine genre clusters.
    bpm_data = np.array(all_bpms).reshape(-1, 1)
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(bpm_data)

    # Determine cluster labels for each BPM.
    cluster_labels = kmeans.labels_

    # Create genre directories based on the determined clusters.
    genres = [f"genre{label}" for label in cluster_labels]

    # Visualize the clustering results.
    visualize_clusters(bpm_data, cluster_labels)

# Function to calculate and store BPM data in a JSON file.
def calculate_and_store_bpm_data():
    all_bpms = []

    for root, _, files in os.walk(source_directory):
        for file in files:
            if file.endswith((".mp3", ".ogg", ".flac")):
                song_path = os.path.join(root, file)
                bpm = get_bpm(song_path)

                if bpm is not None:
                    all_bpms.append(bpm)

    if not all_bpms:
        print("No BPM values found in the songs.")
        return

    with open(bpm_data_file, "w") as file:
        json.dump(all_bpms, file)

# Function to read BPM data from a JSON file.
def read_bpm_data():
    if os.path.exists(bpm_data_file):
        with open(bpm_data_file, "r") as file:
            return json.load(file)
    return []

# Function to create artist-specific folders and move songs to those folders within a genre directory.
def organize_songs_by_genre():
    no_bpm_list = []

    for root, _, files in os.walk(source_directory):
        for file in files:
            if file.endswith(".mp3"):
                song_path = os.path.join(root, file)

                bpm = get_bpm(song_path)

                if bpm is not None:                    
                    for genre, (min_bpm, max_bpm) in genre_directories.items():
                        if min_bpm <= bpm <= max_bpm:
                            if "djvinylo" in song_path and genre == "dnb":
                                print("Maybe not dnb")
                            else:
                                move_song(file, song_path, genre)
                else:
                    #print(f"{song_path} is {genre}")
                    no_bpm_list.append(song_path)
    
    print(f"Unidentified: {no_bpm_list}")

# Function to create artist-specific folders and move songs to those folders within a genre directory.
def organize_songs_by_artist_in_genre(genre_directory):
    for root, _, files in os.walk(os.path.join(source_directory, genre_directory)):
        for file in files:
            if file.endswith(".mp3"):
                song_path = os.path.join(root, file)

                # Check if the parent directory matches the genre directory.
                parent_directory = os.path.basename(os.path.dirname(song_path))
                if parent_directory == genre_directory:
                    try:
                        artist_name, _ = file.split(" - ", 1)
                        artist_directory = os.path.join(root, artist_name)
                    except ValueError as ve:
                        print("Song not in {artist - song} format")
                    if not os.path.exists(artist_directory):
                        os.mkdir(artist_directory)
                    move_song(file, song_path, os.path.join(genre_directory, artist_name))

def main():
    
    create_genre_directories()

    #organize_songs_by_genre()

    # Organize songs by artist within each genre directory.
    for genre in genre_directories.keys():
        organize_songs_by_artist_in_genre(genre)

if __name__ == "__main__":
    main()
