# export-kobo-to-notion
export-kobo-to-notion
![image](https://github.com/gtemta/export-kobo-to-notion/assets/12581990/7d5a85d2-34dc-4e28-9c1e-782c9139300e)
A Node script that exports Kobo highlights to a Notion database. This is base on juliariec's export-kobo-to-notion (https://github.com/juliariec/export-kobo-to-notion)

## Prerequisites

You'll need [Git](https://git-scm.com/downloads) and [Node](https://nodejs.org/en/) installed on your computer.

You'll also need to configure a Notion "integration" that has access to the database you wish to use (your "library" database). Notion has instructions on how to set up an integration [here](https://developers.notion.com/docs#step-1-create-an-integration), and you can give it access to your library database by sharing the database with the integration.


## How to use this script

1. In your terminal, clone this repository by running the following command:

   ```
   git clone https://github.com/juliariec/export-kobo-to-notion.git
   ```

1. Navigate inside the folder and run `npm install` to install the necessary modules.

1. Create a file called `.env`. Inside the file, you'll need to set two variables:

   1. `NOTION_TOKEN`, which is the internal integration token associated with your Notion integration. You can find this [here](https://www.notion.so/my-integrations), and it will look like `secret_TY78iopwv` (but longer).
   2. `NOTION_DATABASE_ID`, which is the ID of the library database. You can find this in the URL of the database page: the URL will have a 32 digit ID located between your workspace name and the ? symbol: it will look like `https://www.notion.so/username/776yv4nanf6qx0bdttznd9upfljupb11?v=s9...`, where the ID is `776yv4nanf6qx0bdttznd9upfljupb11`

   So your `.env` file will look like this:

   ```
   NOTION_TOKEN=secret_TY78iopwv
   NOTION_DATABASE_ID=776yv4nanf6qx0bdttznd9upfljupb11
   ```

1. Connect your Kobo to your computer and open it in File Explorer. Navigate into the `.kobo` directory and copy the file called `KoboReader.sqlite`, and then paste it into the `export-kobo-to-notion` folder.

1. Go to your Notion library database and make sure that the database contains a "Title" property with the name of the book, and a "Exported" checkbox property which defaults to unchecked. (The script will match books based on the title, and then see if highlights have already been uploaded: if not, it will upload them, and then set the "Exported" box to checked).

1. Run the script with the command `npm start`, and then check your Notion database to confirm that it worked.


https://github.com/gtemta/export-kobo-to-notion/assets/12581990/e3670444-6483-43b2-9b67-ec500d68507e


3. The Script should be able to get book title and hightlights from highlights.sqlite.
4. Create new Entry for unsynced books then sync the highlight for them.

## Sync Content
1. Book name
2. Last Read name
3. Exported (If you want to resync the highlight, make the check box unchecked)
