import requests
from bs4 import BeautifulSoup
import ast
import os
import time
import urllib
import aiohttp
import asyncio
import sys
import emoji

def get_download_data(song_name):

    #song_name = song_name.replace("&","%26")

    search_url = f"https://slider.kz/vk_auth.php?q={song_name.replace(' ', '%20')}"
    headers = {
        "Referer": "https://slider.kz/"
    }
    print("SEARCH URL: " + search_url)
    response = requests.get(search_url, headers=headers)
    return response.json()

def get_song_download_links(song):

    song_name = song["name"]
    song_user = song["user"]

    if '-' not in song_name:
        song_name = song_user + " " + song_name

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

    if not os.path.exists("songs"):
        os.mkdir("songs")
    
    if not os.path.exists(f"songs/{path}"):
        os.mkdir(f"songs/{path}")
    
    if not os.path.isfile(f"songs/{path}/{file_name}.mp3"):

        if 'https' not in download_link:
            download_link = "https://slider.kz/" + download_link

        response = requests.get(download_link)

        with open(f"songs/{path}/{file_name}.mp3", "wb") as f:
            f.write(response.content)

        print(f"Downloaded {file_name}")
        print()
    else:
        print(f"{file_name} already downloaded")
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

def load_txt_from_file(filename):
    #Read the contents of the file and load them into a list
    with open(filename, 'r', encoding='utf-8') as file:
        txt = file.read().splitlines()
    return txt

def save_dict_to_file(filename, dict):

    # Write the dictionary as a string to a file    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(str(dict))
        print(f'Dictionary written to {filename}')

def load_dict_from_file(filename):
    # Open the file in read mode with utf-8 encoding
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Use ast.literal_eval() to safely convert the content back to a dictionary
    try:
        loaded_data = ast.literal_eval(content)
        dictionary_string_print = f"Dictionary loaded successfully."
        print(dictionary_string_print)
        print("-" * len(dictionary_string_print))
    except (ValueError, SyntaxError):
        loaded_data = None
        print("Error loading the dictionary from the file.")
    
    return loaded_data

async def download_song_async(file_name, download_link, path):

    file_name = file_name.replace('?','').replace('>','')

    if not os.path.exists("songs"):
        os.mkdir("songs")

    if not os.path.exists(f"songs/{path}"):
        os.mkdir(f"songs/{path}")

    if not os.path.isfile(f"songs/{path}/{file_name}.mp3"):
        if 'https' not in download_link:
            download_link = "https://slider.kz/" + download_link

        async with aiohttp.ClientSession() as session:
            async with session.get(download_link) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(f"songs/{path}/{file_name}.mp3", "wb") as f:
                        f.write(content)
                    print(f"Downloaded {file_name}")
                    print()
                else:
                    print(f"Failed to download {file_name}. Status code: {response.status}")
    else:
        print(f"{file_name} already downloaded")
        print()

async def main():

    # name = "Freestylers & MC Spyda - My Sound (TOMY RMX)"
    # user = "TOMY"
    # song = {"name":name, "user":user}
    # d_data = get_download_data(name)["audios"][""]

    # for link in d_data:
    #     print(link["tit_art"])
    # print(len(d_data))

    likes_to_download = 'likes.txt'
    links_file_name = f'{likes_to_download.replace(".txt","")}_download_links.txt'

    # If download links file doesn't exist fetch songs
    if not os.path.isfile(links_file_name):

        #Read the contents of the file and load them into a list
        song_file = load_txt_from_file(likes_to_download)
        
        # Clean up song names
        song_file_clean = []
        strings_to_replace = ["!", "¡", "·", "*", "⫷", "⫸", '"', '&', '#', '@'
                            "[YA A LA VENTA]", "YA A LA VENTA",  
                            "[YA DISPONIBLE]", "[Ya Disponible]", "Ya disponible",
                            "[FREE DOWNLOAD]", "[Free Download]", "[Free DL]", 
                            "(FREE DOWNLOAD)", "( FREE DOWNLOAD )", "(Free Download)", 
                            "Free DL", "Free Download", "FREE DOWNLOAD", "FREE DL",
                            "[OUT NOW]", "[ OUT NOW ]", "[Out Now]", "OUT NOW", "Out Now", "Out now",
                            "[PREMIERE]",
                            "BEATPORT", "BANDCAMP", 
                            "(Patreon Exclusive)", "[PATREON EXCLUSIVE]", "PATREON",
                            "ON",  "(Original Mix)",
                            "[","]", "     ", "    ", "   ", "  "                            
                            ]
        
        for song in song_file.copy():   
            # Remove emojis and strings
            song = ''.join(c for c in song if c not in emoji.EMOJI_DATA)
            for string in strings_to_replace:
                if string in song:
                    song = song.replace(string,"")
                    print(f"Replaced {string} {song}")
        
            song_file_clean.append(song)
        
        # Open the file in write mode and write the list to it
        # with open("cleanup.txt", "w") as file:
        #     for item in song_file_clean:
        #         file.write(item + "\n")

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
            print("-"*50)
            i = i +1

            # Save every 5 songs
            if i % 5 == 0:
                save_dict_to_file(links_file_name, download_links)

        # Write the dictionary as a string to a file    
        save_dict_to_file(links_file_name, download_links)
    
    else:

        loaded_data = load_dict_from_file(links_file_name)

        # Quick reformat
        # changes_made = False
        # for song, links in loaded_data.items():

        #     for link in links[0:10]:
        #         if "downloaded" in link:
        #             link.pop("downloaded")
        #             changes_made = True
            
        #     if "downloaded" not in links:
        #         loaded_data[song].append({"downloaded" : False})
        #         changes_made = True

        # if changes_made:
        #     save_dict_to_file(links_file_name, loaded_data)
        # Now you can work with the loaded_data dictionary

        for song, links in loaded_data.items():

            song_user = song.split(",")[0]
            song_name = song.split(",")[1]

            if len(links) > 0 and 'downloaded' in links[-1] and links[-1]['downloaded'] != False:
                temp_string = f"{song_name} already downloaded as {links[-1]['downloaded']}"
                print(temp_string)
                print("-" * len(temp_string))
                continue

            if len(links) == 0:
                print(f"{song_name} was not found")
                continue
            
            elif len(links) >= 1:
                
                # Download if song name == current song and bitrate >= 320
                print(song_user + ", " + song_name)
                print("-" * len(song_user + " " + song_name))

                # Initialize variables to track the longest track's length and index
                longest_length = 0
                longest_index = -1

                for i, links_data in enumerate(links):
                    if 'name' not in links_data:
                        break
                    if links_data['name'] == song_name and links_data['bitrate'] is not None and links_data['bitrate'] >= 320:
                        if links_data['length'] > longest_length:
                            longest_length = links_data['length']
                            longest_index = i

                if longest_index >= 0:
                    song_data = links[longest_index]
                    song_name = song_data["name"]
                    song_download_link = song_data["url"]
                    await download_song_async(song_name, song_download_link, likes_to_download.split(".txt")[0])
                    loaded_data[song][-1]["downloaded"] = song_name
                    save_dict_to_file(links_file_name, loaded_data)
                else:
                    print("No matching links with sufficient bitrate found.")

                # Old behavior let's you choose one by one which track you want, takes a long time
                #
                # for i, links_data in enumerate(links, start=1):
                #     if i < 10:
                #         print(f"{i}. {links_data['name']:<99} || {int_to_min_seconds(links_data['length'])} || {links_data['bitrate']}kbps")
                #     elif i == 10:
                #         print(f"{i}. {links_data['name']:<98} || {int_to_min_seconds(links_data['length'])} || {links_data['bitrate']}kbps")

                # while True:
                #     try:
                #         link_index = int(input("Enter the number of the link you want to download (0 to skip): "))
                #         if link_index == 0:
                #             break
                #         elif 1 <= link_index <= len(links):
                #             song_name = links[link_index - 1]["name"]
                #             song_download_link = links[link_index - 1]["url"]
                #             await download_song_async(song_name, song_download_link, likes_to_download.split(".txt")[0])
                #             #download_song(song_name, song_download_link, likes_to_download.split(".txt")[0])
                #             loaded_data[song][-1]["downloaded"] = song_name
                #             save_dict_to_file(links_file_name, loaded_data)
                #             break
                #         else:
                #             print("Invalid choice. Please enter a valid number.")
                #     except ValueError:
                #         print("Invalid input. Please enter a number.")

                # print()  # Empty line for readability

if __name__ == "__main__":
    asyncio.run(main())