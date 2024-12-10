 
import cv2
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, Label
import zipfile
import os

# Function to crop and resize an image to 100x100 pixels
def crop_and_resize(image):
    # Convert the image to grayscale and apply binary thresholding
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours in the binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If no contours are found, return None
    if not contours:
        messagebox.showwarning("No Character Found", "No character detected in the image.")
        return None

    # Sort contours by area in descending order and select the largest one
    largest_contour = max(contours, key=cv2.contourArea)

    # Set a minimum area threshold to avoid processing small noise
    min_area_threshold = 100  # Adjust based on image quality

    # Ensure the largest contour meets the minimum area requirement
    if cv2.contourArea(largest_contour) < min_area_threshold:
        messagebox.showwarning("No Valid Character Found", "The detected contour is too small.")
        return None

    # Calculate the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Apply padding to the bounding box (ensure it stays within image bounds)
    padding = 5
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(w + padding * 2, image.width - x)
    h = min(h + padding * 2, image.height - y)

    # Crop and resize the image to 100x100 pixels
    cropped_img = image.crop((x, y, x + w, y + h))
    resized_img = cropped_img.resize((100, 100), Image.LANCZOS)

    return resized_img

# Function to process the uploaded images
def process_images():
    # Allow users to upload multiple images
    file_paths = filedialog.askopenfilenames(title="Select Images", 
                                             filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if not file_paths:
        messagebox.showwarning("No File Selected", "Please select at least one image.")
        return

    # Create a folder for processed images if it doesn't exist
    if not os.path.exists("processed_images"):
        os.mkdir("processed_images")

    # Process each uploaded image and save exactly one output per input image
    for file_path in file_paths:
        image = Image.open(file_path)
        processed_image = crop_and_resize(image)

        if processed_image:  # Save the image only if processing is successful
            output_path = os.path.join("processed_images", os.path.basename(file_path))
            processed_image.save(output_path, "JPEG")

    messagebox.showinfo("Success", "Images processed successfully!")

# Function to create a ZIP file with the processed images and clear the folder afterward
def create_zip():
    zip_filename = filedialog.asksaveasfilename(defaultextension=".zip", 
                                                filetypes=[("ZIP Files", "*.zip")])
    if not zip_filename:
        return  # User cancelled

    # Create a ZIP file with processed images
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files_list in os.walk("processed_images"):
            for file in files_list:
                zf.write(os.path.join(root, file), file)

    messagebox.showinfo("Success", f"ZIP file saved as {zip_filename}")

    # Clear the processed_images folder
    for root, _, files_list in os.walk("processed_images"):
        for file in files_list:
            os.remove(os.path.join(root, file))
    
    # Optionally, remove the processed_images directory itself if it's empty
    if not os.listdir("processed_images"):
        os.rmdir("processed_images")

    messagebox.showinfo("Cleared", "Processed images folder has been cleared.")

# GUI Setup using Tkinter
root = tk.Tk()
root.title("Bengali Character Cropper and Resizer")
root.geometry("500x300")

# Set Background Color
background_color = "#ffd166"
root.configure(bg=background_color)

# Watermark Label
watermark = Label(root, text="24 Dataset\nDeveloped by Mehedi Hasan", 
                  font=("Arial", 12, "italic"), fg="gray", bg=background_color)
watermark.place(x=10, y=10)

# Header Label
header = Label(root, text="Bengali Character Cropper and Resizer", 
               font=("Helvetica", 16, "bold"), fg="#073B4C", bg=background_color)
header.pack(pady=10)

# Upload Button
upload_button = tk.Button(root, text="Upload and Process Images", 
                          command=process_images, font=("Arial", 14), 
                          bg="#87CEEB", fg="black", activebackground="#00BFFF")
upload_button.pack(pady=10)

# ZIP Button
zip_button = tk.Button(root, text="Create ZIP File", 
                       command=create_zip, font=("Arial", 14), 
                       bg="#FFB6C1", fg="black", activebackground="#FF69B4")
zip_button.pack(pady=10)

# Footer Label
footer = Label(root, text="Upload images, crop characters, and download ZIP files easily!", 
               font=("Arial", 10), fg="#333333", bg=background_color)
footer.pack(side="bottom", pady=10)

# Run the application
root.mainloop()

