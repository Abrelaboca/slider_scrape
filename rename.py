import os

def rename_files_in_directory(directory):
    try:
        # List all files and subdirectories in the current directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)

            # Check if the item is a file
            if os.path.isfile(item_path):
                
                if ' [www.slider.kz]' in item:
                    # Remove the string '[www.slider.kz]' from the file name
                    new_name = item.replace(' [www.slider.kz]', '')
                    new_path = os.path.join(directory, new_name)

                    # Rename the file safely
                    os.rename(item_path, new_path)
                    print(f'Renamed: {item} -> {new_name}')

            # If the item is a directory, recursively process it
            elif os.path.isdir(item_path):
                rename_files_in_directory(item_path)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Prompt the user for the directory path
    directory_path = input("Enter the directory path: ")

    # Check if the provided path exists
    if not os.path.exists(directory_path):
        print("The specified directory path does not exist.")
    else:
        # Start renaming files in the specified directory and its subdirectories
        rename_files_in_directory(directory_path)
