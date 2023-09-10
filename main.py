import requests
from bs4 import BeautifulSoup
import ast
import os
import time
import urllib

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

    #can_get_bitrate = True

    data = get_download_data(song_name)
    #Try to add user if song name didn't return any results
    for audio_info in data["audios"][""]:
        if len(audio_info) == 0:
            #if song_user not in song_name:
            data = get_download_data(song_user + " " + song_name)

    download_links = []
    slice = data["audios"][""][0:10]
    
    for audio_info in slice:
        # No results even with user
        if len(audio_info) == 0:
            print(f"\t {song_name} NOT FOUND")
        else:
            # Get bit rate        
            url = audio_info["url"]
            name = audio_info["tit_art"]
            length = audio_info["duration"]

            if 'https' not in url:
                url = "https://slider.kz/" + url

            #if can_get_bitrate:
            try:
                
                tic = time.perf_counter()            
                size = urllib.request.urlopen(url.replace(" ", "%20")).info()["Content-Length"]               
                #size = requests.head(url).headers["Content-Length"]
                toc = time.perf_counter()
                print(f"Fetched bitrate in {toc - tic:0.2f} seconds")
                bitrate = (int(size)/1000)/length*8
                bitrate = round(bitrate,0)
                bitrate = int(bitrate)
            except Exception as e:
                print(f"\t Couldn't get bitrate of {name}")
                #can_get_bitrate = False
                bitrate = None

            download_links.append({"name" : name, "url" : url, "length" : length, "bitrate" : bitrate, "downloaded" : False})

    return download_links

def download_song(file_name, download_link, path):

    if 'https' not in download_link:
        download_link = "https://slider.kz/" + download_link

    response = requests.get(download_link)

    if not os.path.exists("songs"):
        os.mkdir("songs")
    
    if not os.path.exists(f"songs/{path}"):
        os.mkdir(f"songs/{path}")
    
    if not os.path.isfile(f"songs/{path}/{file_name}.mp3"):

        with open(f"songs/{path}/{file_name}.mp3", "wb") as f:
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

def int_to_min_seconds(seconds):
    # Calculate minutes and remaining seconds
    minutes = seconds // 60
    remaining_seconds = seconds % 60

    # Format the result as a string
    time_string = f"{minutes:02}:{remaining_seconds:02}"

    return time_string

if __name__ == "__main__":

    likes_to_download = 'likes_bowser.txt'
    links_file_name = f'{likes_to_download.replace(".txt","")}_download_links.txt'

    # If download links file doesn't exist fetch songs
    if not os.path.isfile(links_file_name):

        #Read the contents of the file and load them into a list
        with open(likes_to_download, 'r', encoding='utf-8') as file:
            song_file = file.read().splitlines()
        
        # Clean up song names
        song_file_clean = []
        strings_to_replace = ["!", "¡", "·", "*", "⫷", "⫸", '"',
                            "[YA A LA VENTA]", "YA A LA VENTA",  
                            "[YA DISPONIBLE]", "[Ya Disponible]", "Ya disponible",
                            "[FREE DOWNLOAD]", "[Free Download]", "[Free DL]", 
                            "(FREE DOWNLOAD)", "( FREE DOWNLOAD )", "(Free Download)", 
                            "Free DL", "Free Download", "FREE DOWNLOAD", "FREE DL",
                            "[OUT NOW]", "[ OUT NOW ]", "[Out Now]", "OUT NOW", "Out Now", 
                            "[PREMIERE]",
                            "BEATPORT", "BANDCAMP", 
                            "(Patreon Exclusive)", "[PATREON EXCLUSIVE]", "PATREON",
                            "ON",
                            "[","]"
                            ]
        for song in song_file.copy():   

            # Remove emojis
            song = song.encode('ascii', 'ignore').decode('ascii')     
            # Remove unnecesary strings
            for string in strings_to_replace:
                if string in song:
                    song = song.replace(string,"")
                    print(f"Replaced {string} {song}")
        
            song_file_clean.append(song)

        # Separate user which uploaded from song name
        song_list = []
        for song in song_file_clean:
            user = song.split(",")[0]
            song_name = song.split(",")[1].replace('!', "")
            song_list.append({"user" : user, "name" : song_name})

        # Fetch download links
        download_links = {}
        print("Obtaining download links")
        n = len(song_file_clean)
        i = 1
        for song in song_list:
            tic = time.perf_counter()
            # Join user again for retrying in download
            download_links[song["user"] + "," + song["name"]] = get_song_download_links(song)     
            toc = time.perf_counter()
            print(f"Fetched {song['name']} in {toc - tic:0.2f} seconds")
            print(f"Progress {i}/{n}")
            i = i +1

        # Write the dictionary as a string to a file    
        with open(links_file_name, 'w', encoding='utf-8') as file:
            file.write(str(download_links))
            print(f'Dictionary written to {links_file_name}')
    
    else:
        # Open the file in read mode with utf-8 encoding
        with open(links_file_name, 'r', encoding='utf-8') as file:
            content = file.read()

        # Use ast.literal_eval() to safely convert the content back to a dictionary
        try:
            loaded_data = ast.literal_eval(content)
            dictionary_string_print = f"{likes_to_download} Dictionary loaded successfully."
            print()
            print(dictionary_string_print)
            print("-" * len(dictionary_string_print))
        except (ValueError, SyntaxError):
            print("Error loading the dictionary from the file.")

        # Now you can work with the loaded_data dictionary
        for song, links in loaded_data.items():

            song_user = song.split(",")[0]
            song_name = song.split(",")[1]

            if len(links) == 0:
                print(f"{song_name} was not found")
                print()

            # elif len(value) == 1:
            #     song_name = value[0][0]
            #     song_download_link = value[0][1]
            #     download_song(song_name, song_download_link)

            elif len(links) >= 1:
                
                print(song_user + " " + song_name)
                print("-" * len(song_user + " " + song_name))

                for i, links_data in enumerate(links, start=1):
                    if i != 10:
                        print(f"{i}. {links_data['name']:<75} || {int_to_min_seconds(links_data['length'])} || {links_data['bitrate']}kbps")
                    else:
                        print(f"{i}. {links_data['name']:<74} || {int_to_min_seconds(links_data['length'])} || {links_data['bitrate']}kbps")

                while True:
                    try:
                        link_index = int(input("Enter the number of the link you want to download (0 to skip): "))
                        if link_index == 0:
                            break
                        elif 1 <= link_index <= len(links):
                            song_name = links[link_index - 1][0]
                            song_download_link = links[link_index - 1][1]                        
                            download_song(song_name, song_download_link, likes_to_download.split(".txt")[0])
                            break
                        else:
                            print("Invalid choice. Please enter a valid number.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

                print()  # Empty line for readability