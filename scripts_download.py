import requests
import os

def download_excel_file(url):
    # Send a GET request to the URL
    response = requests.get(url)
    if response.status_code == 200:
        # Extract the filename from the URL
        filename = url.split("/")[-1]

        # Get the current working directory
        current_dir = os.getcwd()

        # Define the path to save the file
        save_path = os.path.join(current_dir, filename)

        # Save the file
        with open(save_path, "wb") as file:
            file.write(response.content)
        
        print("Excel file downloaded and saved successfully.")
    else:
        print("Failed to download the Excel file.")

def main():
    url = "https://images.5paisa.com/website/scripmaster-csv-format.csv"
    download_excel_file(url)

if __name__ == "__main__":
    main()



