# backend/main.py (continue from above)

@app.get("/api/data/files", response_model=list[FileMetadata])
async def list_data_files():
    """
    Scans the 'data' directory and returns a list of CSV file metadata.
    """
    data_dir = "data" # Path to your data folder within scraper-be
    files_list = []
    file_id = 1

    if not os.path.exists(data_dir):
        return [] # Return empty list if directory doesn't exist

    for filename in os.listdir(data_dir):
        if filename.endswith(".csv"): # Only process CSV files
            file_path = os.path.join(data_dir, filename)

            # Try to extract date from filename (e.g., D1_full_31_05.csv -> 31_05)
            # You might need to adjust this logic based on your actual naming convention
            file_date = "Unknown Date"
            try:
                # Assuming format like D*_full_DD_MM.csv or D*_link_DD_MM.csv
                parts = filename.split('_')
                if len(parts) >= 3:
                    date_part = parts[-2] + '_' + parts[-1].split('.')[0] # e.g., '31_05'
                    # Attempt to parse as DD_MM and format as YYYY-MM-DD (current year)
                    # Set to 2025 as the context date is in 2025
                    file_date_obj = datetime.strptime(date_part + '_2025', '%d_%m_%Y')
                    file_date = file_date_obj.strftime('%Y-%m-%d')
                else:
                    # Fallback for other naming conventions or generated files
                    # Get creation/modification time if date is not in filename
                    timestamp = os.path.getmtime(file_path) # get modification time
                    file_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            except Exception:
                # If date parsing fails, use a fallback
                timestamp = os.path.getmtime(file_path) # get modification time
                file_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

            # For item count, you'd typically read the CSV and count rows,
            # but for simplicity, we can initially just show a placeholder or 0.
            # Reading entire CSV for count on every API call might be slow for many/large files.
            # For now, let's assume 0, or you can implement a quick row count.
            item_count = 0 
            # Example of counting lines (excluding header, if any) - might be slow for large files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    item_count = sum(1 for line in f) - 1 # Subtract 1 for header row
                    if item_count < 0: item_count = 0
            except Exception:
                pass # Keep item_count as 0 if reading fails

            files_list.append(
                FileMetadata(
                    id=file_id,
                    name=filename,
                    date=file_date,
                    itemCount=item_count,
                    path=file_path # Store full path for later use
                )
            )
            file_id += 1

    # Sort files by date, newest first
    files_list.sort(key=lambda f: f.date, reverse=True)

    return files_list