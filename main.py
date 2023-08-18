import requests

def get_song_download_links(song_name):
    search_url = f"https://slider.kz/vk_auth.php?q={song_name.replace(' ', '%20')}"
    headers = {
        "Referer": "https://slider.kz/"
    }
    response = requests.get(search_url, headers=headers)
    data = response.json()

    download_links = []
    for audio_info in data["audios"][""]:
        download_links.append(audio_info["url"])

    return download_links

def download_song(download_link, file_name):

    response = requests.get(download_link)
    
    with open(file_name, "wb") as f:
        f.write(response.content)

if __name__ == "__main__":

    song_names = []
    
    #song_names = ['papi chulo ukg']  # Replace with your list of song names
    
    for song_name in song_names:
        download_links = get_song_download_links(song_name)
        
        for idx, download_link in enumerate(download_links, start=1):
            file_name = f"{song_name}_{idx}.mp3"
            download_song(download_link, file_name)
            print(f"Downloaded {file_name}")
