import os
import time
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to save pages as PDF
def save_pages_as_pdf(main_url, save_folder):
    # Set up Selenium WebDriver options for headless mode
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-print-browser")

    # Start WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(main_url)

    # Scroll to ensure all content is loaded
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(50)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Parse the main page to find project links
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    project_link_tags = [h4.find('a')['href'] for h4 in soup.find_all('h4', class_='title') if h4.find('a')]
    driver.quit()

    # Iterate over each project link and save as PDF
    for count, link in enumerate(project_link_tags, start=1):
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(link)
        time.sleep(50)

        # Save the current page as a PDF
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,
            "preferCSSPageSize": True
        })

        pdf_path = os.path.join(save_folder, f"project_{count}.pdf")
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(base64.b64decode(pdf_data['data']))

        print(f"Saved: {pdf_path}")
        driver.quit()
        time.sleep(1)

    messagebox.showinfo("Success", f"Saved {len(project_link_tags)} projects as PDFs in {save_folder}")

# Function to choose save directory and start download
def choose_directory_and_download():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a URL.")
        return
    
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        save_pages_as_pdf(url, folder_selected)

# Set up the Tkinter GUI
root = tk.Tk()
root.title("Project Page PDF Downloader")

frame = tk.Frame(root)
frame.pack(pady=10)

url_label = tk.Label(frame, text="Enter URL:")
url_label.pack(side="left")
url_entry = tk.Entry(frame, width=50)
url_entry.pack(side="left", padx=5)

download_button = tk.Button(root, text="Choose Directory and Download", command=choose_directory_and_download)
download_button.pack(pady=10)

root.mainloop()
