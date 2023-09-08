import requests
from bs4 import BeautifulSoup
import ast
import os
import urllib
from progress.bar import Bar
import re

def get_download_data(song_name):

    search_url = f"https://slider.kz/vk_auth.php?q={song_name.replace(' ', '%20')}"
    headers = {
        "Referer": "https://slider.kz/"
    }
    response = requests.get(search_url, headers=headers)
    return response.json()

def get_song_download_links(song):

    song_name = song["name"]
    song_user = song["user"]

    can_get_bitrate = True

    data = get_download_data(song_name)
    #Try to add user if song name didn't return any results
    for audio_info in data["audios"][""]:
        if len(audio_info) == 0:
            if song_user not in song_name:
                data = get_download_data(song_user + " " + song_name)

    download_links = []
    for audio_info in data["audios"][""]:
        # No results even with user
        if len(audio_info) == 0:
            print(f"{song_name} NOT FOUND")
        else:
            # Get bit rate        
            url = audio_info["url"]
            name = audio_info["tit_art"]
            length = audio_info["duration"]

            if 'https' not in url:
                url = "https://slider.kz/" + url

            if can_get_bitrate:
                try:
                    size = urllib.request.urlopen(url.replace(" ", "%20")).info()["Content-Length"]
                    bitrate = (int(size)/1000)/length*8
                    bitrate = round(bitrate,0)
                    bitrate = int(bitrate)
                except Exception as e:
                    print(f"\t Couldn't get bitrate of {song_name}")
                    can_get_bitrate = False
                    bitrate = None
            else:
                bitrate = None

            download_links.append({"name" : name, "url" : url, "length" : length, "bitrate" : bitrate, "downloaded" : False})

    return download_links

def download_song(file_name, download_link):

    if 'https' not in download_link:
        download_link = "https://slider.kz/" + download_link

    response = requests.get(download_link)

    if not os.path.exists("songs"):
        os.mkdir("songs")
    
    if not os.path.isfile(f"songs/{file_name}.mp3"):

        with open(f"songs/{file_name}.mp3", "wb") as f:
            f.write(response.content)

        print(f"Downloaded {song_name}")
        print()
    else:
        print(f"{song_name} already downloaded")
        print()

def get_song_names(user):

    search_url = f"https://soundcloud.com/{user}/likes"
    
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, "html.parser")    

    song_names = []
    song_elements = soup.find_all("h2", itemprop="name")

    for song_element in song_elements:
        song_name = song_element.a.get_text(strip=True)
        song_names.append(song_name)
    
    return song_names

if __name__ == "__main__":

    likes_to_download = 'likes.txt'

    #Read the contents of the file and load them into a list
    with open(likes_to_download, 'r', encoding='utf-8') as file:
        song_file = file.read().splitlines()
    
    song_file_clean = []
    strings_to_replace = ["!", "YA A LA VENTA", "[", "]", "Free DL", "Free Download", "OUT NOW", "BEATPORT", "Ya disponible"]

    for song in song_file.copy():        
        # Remove unnecesary strings
        for string in strings_to_replace:
            song = song.replace(string,"")
        # Remove emojis
        song_file_clean.append(song.encode('ascii', 'ignore').decode('ascii'))

    # Separate user which uploaded from song name
    song_list = []
    for song in song_file:
        user = song.split(",")[0]
        song_name = song.split(",")[1].replace('!', "")
        song_list.append({"user" : user, "name" : song_name})

    download_links = {}
    print("Obtaining download links")
    with Bar('Processing...') as bar:
        for song in song_list:
            download_links[song["name"]] = get_song_download_links(song)
            bar.next()

    # Open the file in write mode and write the dictionary as a string
    with open(f'{likes_to_download}_download_links.txt', 'w', encoding='utf-8') as file:
        file.write(str(download_links))
        print(f'Dictionary written to {likes_to_download}_download_links.txt')

    # Open the file in read mode with utf-8 encoding
    with open('download_links.txt', 'r', encoding='utf-8') as file:
        content = file.read()

    # Use ast.literal_eval() to safely convert the content back to a dictionary
    try:
        loaded_data = ast.literal_eval(content)
        print("Dictionary loaded successfully.")
    except (ValueError, SyntaxError):
        print("Error loading the dictionary from the file.")

    # Now you can work with the loaded_data dictionary
    for key, value in loaded_data.items():

        if len(value) == 0:
            print(f"{key} was not found")
            print()

        elif len(value) == 1:
            song_name = value[0][0]
            song_download_link = value[0][1]
            download_song(song_name, song_download_link)

        elif len(value) > 1:
            print(f"{key} has multiple links") #"Has multiple links"

            for i, (description, link) in enumerate(value, start=1):
                print(f"{i}. {description}")
                # Prompt the user to select a link
            while True:
                try:
                    choice = int(input("Enter the number of the link you want to download (0 to skip): "))
                    if choice == 0:
                        break
                    elif 1 <= choice <= len(value):
                        song_name = value[choice - 1][0]
                        song_download_link = value[choice - 1][1]                        
                        download_song(song_name, song_download_link)
                        break
                    else:
                        print("Invalid choice. Please enter a valid number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            print()  # Empty line for readability

