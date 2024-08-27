# Export Kobo Highlights to Notion

Automatically export Kobo highlights to a Notion database using Python. This project is inspired by and builds upon juliariec's `export-kobo-to-notion` written in JavaScript.

![Project Image](https://github.com/gtemta/export-kobo-to-notion/assets/12581990/7d5a85d2-34dc-4e28-9c1e-782c9139300e)

## Prerequisites

Before you start, make sure you have the following installed:

- [Python](https://www.python.org/) for automating the retrieval of .sqlite data.

Additionally, you'll need to set up a Notion integration with access to your target database. Follow Notion's guide for creating an integration [here](https://developers.notion.com/docs#step-1-create-an-integration) and share your library database with this integration.

## How to Use This Script

1. Clone this repository:

   ```
   git clone https://github.com/gtemta/export-kobo-to-notion.git
   ```

2. Inside the cloned directory, install the necessary modules:
   ```
   pip install -r requirements.txt
   ```

3. Create a .env file with the following content:

NOTION_TOKEN: Your Notion integration token. Find it here.
NOTION_DATABASE_ID: The ID of your Notion library database. Extract it from the database page URL.
Example .env file:

- `NOTION_TOKEN`: Your Notion integration token. Find it [here](https://www.notion.so/my-integrations) 
- `NOTION_DATABASE_ID`: The ID of your Notion library database. Extract it from the database page URL.

Example `.env` file:

   1. `NOTION_TOKEN`, which is the internal integration token associated with your Notion integration. You can find this [here](https://www.notion.so/my-integrations), and it will look like `secret_TY78iopwv` (but longer).
   2. `NOTION_DATABASE_ID`, which is the ID of the library database. You can find this in the URL of the database page: the URL will have a 32 digit ID located between your workspace name and the ? symbol: it will look like `https://www.notion.so/username/776yv4nanf6qx0bdttznd9upfljupb11?v=s9...`, where the ID is `776yv4nanf6qx0bdttznd9upfljupb11`

   So your `.env` file will look like this:

   ```
   NOTION_TOKEN=secret_TY78iopwv
   NOTION_DATABASE_ID=776yv4nanf6qx0bdttznd9upfljupb11
   ```

4. Execute the checkUSBandUpload.py
   ```
   python .\checkUSBandUpload.py
   ```
5. Connect the Kobo EReader to your PC in 1 minutes, the program will detect the usb device.
  (You can also connect it before step 4)

6. Verify the highlights in your Notion database.

## Demo Video
https://github.com/gtemta/export-kobo-to-notion/assets/12581990/edf1d6fc-a091-421b-bff6-b3a6863a9bf3

Personal Example
https://danteyfchen.notion.site/Kobo-EReader-Export-3ef27db4954a4e06b6261b2c5a704a4f?pvs=4



## Script Features
- Retrieves book titles and highlights from `KoboReader.sqlite`.
- Creates new entries for books not yet synced and uploads their highlights.

## Sync Content
- Book name
- Last read Time
- Spend Reading Time
- Exported status (Uncheck to resync highlights)
