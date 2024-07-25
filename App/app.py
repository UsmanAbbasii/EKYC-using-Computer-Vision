import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import pandas as pd
import base64
import re
from datetime import datetime, timedelta
from database import connect, record_exists, insert_record

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)  # Adjust language and GPU setting as needed

# Function to process the image and extract text
def process_image(image):
    # Convert uploaded image to numpy array
    img_np = np.array(image)

    # Reading the image and applying OCR
    result = reader.readtext(img_np)

    # Extracted data dictionary
    extracted_data = {
        "Name": None,
        "Father Name": None,
        "Gender": None,
        "Country of Stay": "Pakistan",  # Default value since it's always Pakistan
        "Identity Number": None,
        "Date of Birth": None,
        "Date of Issue": None,
        "Date of Expiry": None
    }

    # Process each detection to fill extracted_data
    for i, detection in enumerate(result):
        text = detection[1].strip()

        # Check for name and father name
        if "name" in text.lower() and not "father" in text.lower():
            extracted_data["Name"] = result[i+1][1].strip() if i+1 < len(result) else None
        elif "father" in text.lower():
            extracted_data["Father Name"] = result[i+1][1].strip() if i+1 < len(result) else None
        elif text.lower() in ["m", "f"]:
            extracted_data["Gender"] = text.upper()
        
        # Check for identity number
        elif re.match(r'\d{5}-\d{7}-\d', text):
            extracted_data["Identity Number"] = text
        
        # Check for date formats
        elif re.match(r'\d{2}\.\d{2}\.\d{4}', text):
            if extracted_data["Date of Birth"] is None:
                extracted_data["Date of Birth"] = text
            elif extracted_data["Date of Issue"] is None:
                extracted_data["Date of Issue"] = text

    # Calculate Date of Expiry if not extracted
    if extracted_data["Date of Issue"] and not extracted_data["Date of Expiry"]:
        try:
            date_of_issue = datetime.strptime(extracted_data["Date of Issue"], "%d.%m.%Y")
            date_of_expiry = date_of_issue.replace(year=date_of_issue.year + 10)
            extracted_data["Date of Expiry"] = date_of_expiry.strftime("%d.%m.%Y")
        except ValueError:
            pass  # Handle the case where Date of Issue cannot be parsed

    return extracted_data

# Function to display extracted data in a table
def display_table(extracted_data):
    # Prepare data for table display
    fields = ["Name", "Father Name", "Gender", "Country of Stay", "Identity Number", "Date of Birth", "Date of Issue", "Date of Expiry"]
    values = [extracted_data[field] if extracted_data[field] else "" for field in fields]
    df = pd.DataFrame(list(zip(fields, values)), columns=['Field', 'Value'])
    st.dataframe(df)

# Function to convert dataframe to CSV and generate download link
def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Encode to base64 (binary to ASCII)
    href = f'<a href="data:file/csv;base64,{b64}" download="extracted_data.csv">Download CSV File</a>'
    return href

def main():
    st.title('ID Card Text Extraction')

    # File uploader
    uploaded_file = st.file_uploader("Upload an image of your ID card", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        # Process the uploaded image and extract text
        extracted_data = process_image(image)

        # Display extracted data in a table
        display_table(extracted_data)

        # Database operations
        connection = connect()
        if connection:
            identity_number = extracted_data["Identity Number"]
            if not record_exists(connection, identity_number):
                insert_record(connection, extracted_data)
                st.success("Data inserted into database.")
            else:
                st.warning("Data already exists in the database.")

            # Provide option to download extracted data as CSV
            st.markdown(get_csv_download_link(pd.DataFrame(list(extracted_data.items()), columns=['Field', 'Value'])), unsafe_allow_html=True)

            # Close connection
            connection.close()
        else:
            st.error("Database connection failed. Check your credentials and database settings.")

if __name__ == '__main__':
    main()
