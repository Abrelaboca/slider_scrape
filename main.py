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
import concurrent.futures
import threading

def get_download_data(song_name):

    #song_name = song_name.replace("&","%26")

    search_url = f"https://slider.kz/vk_auth.php?q={song_name.replace(' ', '%20')}"
    headers = {
        "Referer": "https://slider.kz/"
    }
    #print("SEARCH URL: " + search_url)
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

            tic = time.perf_counter()
            try:                                    
                size = urllib.request.urlopen(url.replace(" ", "%20")).info()["Content-Length"]               
                #size = requests.head(url).headers["Content-Length"]
                bitrate = (int(size)/1000)/length*8
                bitrate = round(bitrate,0)
                bitrate = int(bitrate)
            except Exception as e:
                #print(f"\t Couldn't get bitrate of {name}")
                #can_get_bitrate = False
                bitrate = None

            toc = time.perf_counter()
            print(f"Fetched {name} in {toc - tic:0.2f}s")
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
        #print(f'Dictionary written to {filename}')

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
    
    if not os.path.exists(f"{path}"):
        os.makedirs(f"{path}")

    if not os.path.isfile(f"{path}/{file_name}.mp3"):
        if 'https' not in download_link:
            download_link = "https://slider.kz/" + download_link
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(download_link) as response:
                    if response.status == 200:

                        content = await response.read()

                        with open(f"{path}/{file_name}.mp3", "wb") as f:
                            f.write(content)

                        temp_string = f"Downloaded {file_name}"
                        pretty_print(temp_string)
                    else:
                        temp_string = f"Failed to download {file_name}. Status code: {response.status}"
                        pretty_print(temp_string)
                        return False
        except Exception as e:
            temp_string = f"Error while trying to download {file_name}: {e}"
            pretty_print(temp_string)
            return False
    else:
        temp_string = f"{file_name} already downloaded"
        pretty_print(temp_string)
    
    return True

def get_all_songs(directory, all_songs=None):

    if all_songs is None:
        all_songs = []

    try:
        # List all files and subdirectories in the current directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)

            # Check if the item is a file
            if os.path.isfile(item_path):
                all_songs.append(item.replace(".mp3", ""))

            # If the item is a directory, recursively process it
            elif os.path.isdir(item_path):
                all_songs = get_all_songs(item_path, all_songs)

    except Exception as e:
        print(f"An error occurred while fetching all songs: {e}")

    return all_songs

def jaccard_similarity(str1, str2):
    set1 = set(str1.split())  # Convert the first string to a set of words
    set2 = set(str2.split())  # Convert the second string to a set of words
    intersection = len(set1.intersection(set2))
    union = len(set1) + len(set2) - intersection
    return intersection / union

def pretty_print(string):
    print(string)
    print("-"*len(string))

def get_all_songs_path(directory, all_songs=None):

    if all_songs is None:
        all_songs = []

    try:
        # List all files and subdirectories in the current directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)

            # Check if the item is a file
            if os.path.isfile(item_path):
                all_songs.append(item_path)

            # If the item is a directory, recursively process it
            elif os.path.isdir(item_path):
                all_songs = get_all_songs_path(item_path, all_songs)

    except Exception as e:
        print(f"An error occurred while fetching all songs: {e}")

    return all_songs

async def main():

    # all = get_all_songs_path("songs")
    # duped = []
    # non_duped = []
    # for song in all:
    #     song_name = song.split("\\")[-1].replace(".mp3", "")
    #     if song_name not in non_duped:
    #         non_duped.append(song_name)
    #     else:
    #         duped.append(song)
    # print(duped)
    # sys.exit()

    base_filename = "likes.txt"
    likes_to_download = f'lists/{base_filename}'
    links_file_name = f'links/{base_filename}'
    song_download_path = f'songs/{base_filename.replace(".txt","")}'
    similar_song_download_path = f'songs/{base_filename.replace(".txt","")}/similar'

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
                            "ON", #  "(Original Mix)",
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

        # Separate user which uploaded from song name
        song_list = []
        for song in song_file_clean:
            user = song.split(",")[0]
            song_name = song.split(",")[1].replace('!', "")
            song_list.append({"user" : user, "name" : song_name})

        # Get download links
        print("Obtaining download links")
        download_links = {}

        n = len(song_file_clean)
        i = 1
        save_lock = threading.Lock()

        # Concurrently fetch download links
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # Adjust the max_workers as needed
            futures = {executor.submit(get_song_download_links, song): song for song in song_list}
            for future in concurrent.futures.as_completed(futures):
                song = futures[future]
                try:
                    download_links[song["user"] + "," + song["name"]] = future.result()
                except Exception as e:
                    print(f"Error fetching links for {song['name']}: {e}")

                i += 1
                if i % 5 == 0:
                    with save_lock:
                        print(f"Progress: {i}/{n}")
                        save_dict_to_file(links_file_name, download_links)

        # Write the dictionary to the file after all threads have completed
        with save_lock:
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
        
        all_songs = get_all_songs("songs")
        already_in_library = 0
        already_downloaded = 0
        downloaded = 0
        no_links = 0
        no_name_match = 0
        no_bitrate_match = 0    
        
        non_matching_names = {}

        for song, links in loaded_data.items():

            song_user = song.split(",")[0]
            song_name = song.split(",")[1]

            # If song is already downloaded in another folder skip
            if song_name in all_songs:
                temp_string = f"{song_name} already in library"
                already_in_library += 1
                pretty_print(temp_string)
                continue
            
            # If song already downloaded in this folder skip
            if len(links) > 0 and 'downloaded' in links[-1] and links[-1]['downloaded'] != False:
                temp_string = f"{song_name} already downloaded as {links[-1]['downloaded']}"
                already_downloaded += 1
                pretty_print(temp_string)
                continue
            
            # If no links found skip
            if len(links) == 0:
                temp_string = f"{song_name} was not found"
                no_links += 1
                pretty_print(temp_string)
                continue
            
            elif len(links) >= 1:
                
                # Download if song name == current song and bitrate >= 320
                temp_string = f"Attempting to download {song_name}"
                print(temp_string)

                # Initialize variables to track the longest track's length and index
                longest_length = 0
                longest_index = -1

                similar_longest_length = 0
                similar_longest_index = -1
                similar_max_sim = 0

                name_match = False  # Track if a name match has been found
                bitrate_match = False  # Track if a bitrate match has been found

                # Check if name is equal and bitrate >= 320
                for i, links_data in enumerate(links):

                    # Sometimes no links songs get stuck here
                    if 'name' not in links_data:
                        break

                    searching_song = links_data['name']
                    searching_song = ''.join(c for c in searching_song if c not in emoji.EMOJI_DATA)

                    if searching_song.lower() == song_name.lower():
                        name_match = True
                        if links_data['bitrate'] is not None and links_data['bitrate'] >= 320:
                            bitrate_match = True
                            if links_data['length'] > longest_length:
                                longest_length = links_data['length']
                                longest_index = i
                    else:                    
                        # Calculate jaccard_similarity
                        sim = jaccard_similarity(searching_song.lower(), song_name.lower())
                        if links_data['bitrate'] is not None and links_data['bitrate'] >= 320 and sim > 0.7:
                            if sim >= similar_max_sim:
                                similar_max_sim = sim
                                if links_data['length'] > similar_longest_length:
                                    similar_longest_length = links_data['length']
                                    similar_longest_index = i

                # If from all links there is an index that matches the name and is the longest of them, download
                if longest_index >= 0:
                    song_data = links[longest_index]
                    song_name = song_data["name"]
                    song_download_link = song_data["url"]
                    if await download_song_async(song_name, song_download_link, song_download_path):
                        downloaded += 1
                        loaded_data[song][-1]["downloaded"] = song_name
                        save_dict_to_file(links_file_name, loaded_data)
                # Has non matching names
                elif similar_longest_index >= 0:
                    song_data = links[similar_longest_index]
                    song_name = song_data["name"]
                    song_download_link = song_data["url"]
                    if await download_song_async(song_name, song_download_link, similar_song_download_path):
                        downloaded += 1
                        loaded_data[song][-1]["downloaded"] = song_name
                        save_dict_to_file(links_file_name, loaded_data)
                else:
                    if not name_match:
                        no_name_match += 1  # Increment once per track with no name match
                        temp_string = "No matching links with name similarity."
                    if not bitrate_match:
                        no_bitrate_match += 1  # Increment once per track with no bitrate match
                        temp_string = "No matching links with sufficient bitrate found."
                    pretty_print(temp_string)


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

        # Using f-strings for pretty printing
        print(f"Downloaded: {downloaded}")
        print(f"Already in library: {already_in_library}")
        print(f"Already downloaded: {already_downloaded}")
        print(f"No links: {no_links}")
        print(f"No name match: {no_name_match}")
        print(f"No bitrate match: {no_name_match}")
        print('-'*50)
        
        # After the loop, you can use non_matching_names to see the differences
        if non_matching_names:
            print("Names that don't match:")
            for song_name, non_matching_data in non_matching_names.items():
                matching_data = [data for data in non_matching_data if data['sim'] > 0.7]
                if len(matching_data) > 0:
                    print(f"Song: {song_name}")
                    for data in non_matching_data:
                        if data['sim'] > 0.7:                        
                            #print(data)
                            print(f"\t{data['name']}, Similarity: {data['sim']}")
                    print('-'*50)

if __name__ == "__main__":
    asyncio.run(main())