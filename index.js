require("dotenv").config();
const { NOTION_TOKEN, NOTION_DATABASE_ID } = process.env;
const { Client } = require("@notionhq/client");
const notion = new Client({ auth: NOTION_TOKEN });
const db = require("better-sqlite3")("KoboReader.sqlite");

async function exportHighlights() {
  console.log(`exportHighlights++`)
  const getBookListQuery =
    "SELECT DISTINCT content.ContentId, content.Title, content.Attribution AS Author,content.DateLastRead " +
    "FROM Bookmark INNER JOIN content " +
    "ON Bookmark.VolumeID = content.ContentID " +
    "ORDER BY content.Title";
  const bookList = db.prepare(getBookListQuery).all();

  for (book of bookList) {
    try {
      console.log(`Get ${book.Title} from DB`)
      // Removes subtitles from book title
      if (book.Title.indexOf(":") !== -1) {
        console.log(`${book.Title} Original Book Title`)
        book.Title = book.Title.substring(0, book.Title.indexOf(":"));
        console.log(`${book.Title} Shrink Book Title`)
      }
      let title = book.Title;
      //Check Notion database for the book
      // let response = await notion.databases.query({
      //   database_id: NOTION_DATABASE_ID,
      //   filter: {
      //     and: [
      //       { property: "Title", text: { contains: title } },
      //       { property: "Exported", checkbox: { equals: false } },
      //     ],
      //   },
      // });
      // Check if the book has already synced
      const syncedTarget = await notion.databases.query({
            database_id: NOTION_DATABASE_ID,
            filter: {
              and: [
                { property: "Title", text: { contains: title } },
                { property: "Exported", checkbox: { equals: true } },
              ],
            },
      });
      if (syncedTarget.results?.length === 1) {
        console.log(`Synced ${title} only one found.`);
      } else if (syncedTarget.results?.length > 1) {
        console.log(`Synced ${title} matched multiple items.`);
      } else {
        console.log(`Synced ${title} unexisted.`);
      }
      isTargetSynced = syncedTarget.results?.length === 1;


      let unSyncedTarget = await notion.databases.query({
        database_id: NOTION_DATABASE_ID,
        filter: {
          and: [
            { property: "Title", text: { contains: title } },
            { property: "Exported", checkbox: { equals: false } },
          ],
        },
      });
      if (unSyncedTarget.results?.length === 1) {
        console.log(`Unsynced ${title} only one found.`);
      } else if (unSyncedTarget.results?.length > 1) {
        console.log(`Unsynced ${title} matched multiple items.`);
      } else {
        console.log(`Unsynced ${title} unexisted.`);
      }

      // Use the results to determine status of the book
      var valid = false;
      const unSyncFound = (unSyncedTarget.results?.length === 1);
      if (unSyncFound) {
        valid = true;
      } else if (isTargetSynced) {
        console.log(`${title} synced. Skip Update Notes only Update Date ${book.DateLastRead}`);
        const pageId = syncedTarget.results[0].id;
        // Updates the LastRead date
        await notion.pages.update({
          page_id: pageId,
          properties: {
            LastReadDate: {
              date: {
                start: book.DateLastRead, // 您的日期值
              },
            },
          },
        });
      } else {
        console.log(`${title} unexisted. Try add Entry for it`);
        valid = addEntryByTitle(title);
      }
      if (valid != true && isTargetSynced == false) {
        console.log(`Try Get Again after wait 2 second`);
        await sleep(2000);
        //Check Notion database for the book
        const unSyncedTarget2 = await notion.databases.query({
          database_id: NOTION_DATABASE_ID,
          filter: {
            and: [
              { property: "Title", text: { contains: title } },
              { property: "Exported", checkbox: { equals: false } },
            ],
          },
        });
        const unSyncAdded = (unSyncedTarget2.results?.length === 1);
        unSyncedTarget = unSyncedTarget2;
        if (unSyncAdded){
          valid = true;
        }
      }


      if (valid) {
        console.log(`Start Sync ${title} Highlights`);
        const pageId = unSyncedTarget.results[0].id;
        var blocks = [];

        // Retrieves highlights for the book
        const getHighlightsQuery =
          "SELECT Bookmark.Text FROM Bookmark INNER JOIN content ON Bookmark.VolumeID = content.ContentID " +
          "WHERE content.ContentID = ? " +
          "ORDER BY content.DateCreated DESC";
        const highlightsList = db
          .prepare(getHighlightsQuery)
          .all(book.ContentID);

        // Starts with a block for the heading
        blocks.push({
          object: "block",
          type: "heading_1",
          heading_1: {
            text: [{ type: "text", text: { content: "Highlights" } }],
          },
        });

        // Generates a text block for each highlight
        for (highlight of highlightsList) {
          if (highlight.Text !== null) {
            blocks.push({
              object: "block",
              type: "paragraph",
              paragraph: {
                text: [{ type: "text", text: { content: highlight.Text } }],
              },
            });
          }
          if (blocks.length > 90) {
              console.log(`Over ${blocks.length} append children first`);
              // Appends the blocks to the book page
              await notion.blocks.children.append({
                block_id: pageId,
                children: blocks,
              });            
              blocks = [];
              console.log(`Clear Block to ${blocks.length}`);
          }
        }

        // Appends the blocks to the book page
        await notion.blocks.children.append({
          block_id: pageId,
          children: blocks,
        });

        // Updates the status of the book page
        await notion.pages.update({
          page_id: pageId,
          properties: { Exported: { checkbox: true } },
        });
        console.log(`Uploaded highlights for ${title}.`);
      }
    } catch (error) {
      console.log(`Error with ${book.Title}: `, error);
    }
  }
}
async function addEntryByTitle(bookTitle) {
  try {
    // Create a new entry in the Notion database
    const response = await notion.pages.create ({
      parent: {
        database_id: NOTION_DATABASE_ID
      },
      properties: {
        title: {
          title: [
            {
              text: {
                content: bookTitle
              }
            }
          ]
        }
      }
    });
    console.log(`Entry ${bookTitle} added successfully!`);
    return true;
  } catch (error) {
    console.error('Error adding entry:', error.message);
    return false;
  }
}

function sleep(ms) {
  return new Promise(resolve => {
    setTimeout(resolve, ms);
  });
}

exportHighlights();
