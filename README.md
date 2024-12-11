## X Scraper

This script allows you to scrape tweets using parameters such as keywords, minimum likes, replies, and date ranges. It requires certain authentication tokens from your browser to work.

---

### Features
- **Search Tweets:** Use keywords,from user, date ranges, and engagement metrics (likes, replies) to filter results.
- **Request Limits:** Handles requests efficiently within the platform's constraints.

---

### Requirements
1. **Python**: Make sure Python is installed. The script was tested with version `3.11`.
2. **Authentication Tokens**: The script requires the following from your browser:
   - **Bearer Token**
   - **X-CSRF Token**
   - **Cookies**
  
---

### How to Get Authentication Tokens
To use this script, you'll need to extract tokens from your browser:

1. **Open Developer Tools**:
   - In your browser, press `F12` or `Ctrl + Shift + I` (or `Cmd + Shift + I` on Mac).

2. **Navigate to the Network Tab**:
   - Select Fetch/XHR and look for SearchTimeline request
   ![image](https://github.com/user-attachments/assets/ef2ba69c-5d7c-4085-9a34-9388decf529b)


3. **Find the Necessary Tokens**:
   - Select the headers tab and scroll down to find the **Bearer Token**, **X-CSRF Token**, and **Cookies**.
     - Autorization : select only the token (Without Bearer)
     - ![image](https://github.com/user-attachments/assets/988cef26-0b64-4b32-b734-ef29ac9d23cc)
     - X-CSRF Token :
     - ![image](https://github.com/user-attachments/assets/ffb04bfb-2cb8-46e9-a9b1-4f502578bb51)
     - Cookies : select EVERYTHING. make sure to convert the `"` to `'`.
     - ![image](https://github.com/user-attachments/assets/e1143852-88ed-4da8-b8b2-afa6cdffddaf)
4. **Set these value in scripts/creds.py**
---

### Usage
1. Run the script:
   ```bash
   python tweet_scraper.py -f <fileName without extension>
   ```

2. Customize your search parameters:
   - you can set these parameters in script/x_scraper.py

---

### Request Limits
**Important:** Twitter has limits on how many requests you can make. Based on my experience:
- **Rate Limit:** Up to 50 requests per 15 minutes (for standard API endpoints).
- Each request fetches around 20 tweets, so adjust your search parameters accordingly.

Check your API or session logs if you encounter rate limit errors. Always adhere to platform policies.

---


### Contribution
Feel free to submit issues or pull requests to enhance the functionality of this scraper.

---

### License
This project is licensed under the [MIT License](LICENSE).

