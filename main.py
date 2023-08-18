import requests
from bs4 import BeautifulSoup
import ast
import os

def get_song_download_links(song_name):

    search_url = f"https://slider.kz/vk_auth.php?q={song_name.replace(' ', '%20')}"
    headers = {
        "Referer": "https://slider.kz/"
    }
    response = requests.get(search_url, headers=headers)
    data = response.json()

    download_links = []

    for audio_info in data["audios"][""]:
        if len(audio_info) == 0:
            print(f"{song_name} NOT FOUND")
        else:
            download_links.append((audio_info["tit_art"], audio_info["url"]))

    return download_links

def download_song(file_name, download_link):

    if 'https' not in download_link:
        download_link = "https://slider.kz/" + download_link

    response = requests.get(download_link)

    if not os.path.exists("songs"):
        os.mkdir("songs")
    
    with open(f"songs/{file_name}.mp3", "wb") as f:
        f.write(response.content)

    print(f"Downloaded {song_name}")

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

    #Read the contents of the file and load them into a list
    # with open('likes.txt', 'r', encoding='utf-8') as file:
    #     songs_list = file.read().splitlines()


    # download_links = {}
    # for song_name in songs_list:
    #     download_links[song_name] = get_song_download_links(song_name)

    # # Open the file in write mode and write the dictionary as a string
    # with open('download_links.txt', 'w', encoding='utf-8') as file:
    #     file.write(str(download_links))
    # print(f'Dictionary written to {filename}')

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
    # For example, you can access its keys and values like this:
    for key, value in loaded_data.items():
        if len(value) == 0:
            print() #
        elif len(value) == 1:

            song_name = value[0][0]
            song_download_link = value[0][1]

            if not os.path.isfile(f"songs/{value[0][0]}.mp3"):
                download_song(song_name, song_download_link)
            else:
                print(f"{song_name} already downloaded")

        elif len(value) > 1:
            print() #"Has multiple links"
