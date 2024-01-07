# export-kobo-to-notion
Export Kobo highlights to a Notion database using this Node.js script. This project is inspired by and builds upon juliariec's `export-kobo-to-notion`. 

![Project Image](https://github.com/gtemta/export-kobo-to-notion/assets/12581990/7d5a85d2-34dc-4e28-9c1e-782c9139300e)

## Prerequisites

Before you start, ensure you have these installed:

- [Git](https://git-scm.com/downloads)
- [Node.js](https://nodejs.org/en/)
- [Python] (https://www.python.org/) for automation get .sqlite

Additionally, you'll need to set up a Notion integration with access to your target database. Follow Notion's guide for creating an integration [here](https://developers.notion.com/docs#step-1-create-an-integration), and share your library database with this integration.

## How to Use This Script

1. Clone this repository:

   ```
   git clone https://github.com/gtemta/export-kobo-to-notion.git
   ```

2. Inside the cloned directory, install the necessary modules:
   ```
   npm install
   ```

3. Create a `.env` file with the following content:
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

   4. Get Sqlite you can choose one of way 
   4.a Connect your Kobo device and copy `KoboReader.sqlite` from the `.kobo` directory to the `export-kobo-to-notion` folder.
   4.b Execute to automatic get the sql and run following steps for you
   ```
   python .\checkUSBandUpload.py
   ```

   5. Ensure your Notion library database has these properties:
   - A "Title" property for the book name.
   - An "Exported" checkbox property, defaulting to unchecked.

   6. Run the script:
      ```
      npm start
      ```

   7. Verify the highlights in your Notion database.

![Additional Image](https://github.com/gtemta/export-kobo-to-notion/assets/12581990/e3670444-6483-43b2-9b67-ec500d68507e)

## Script Features
- Retrieves book titles and highlights from `KoboReader.sqlite`.
- Creates new entries for books not yet synced and uploads their highlights.

## Sync Content
- Book name
- Last read position
- Exported status (Uncheck to resync highlights)
