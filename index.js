require("dotenv").config();
const { NOTION_TOKEN, NOTION_DATABASE_ID } = process.env;
const { Client } = require("@notionhq/client");
const notion = new Client({ auth: NOTION_TOKEN });
const db = require("better-sqlite3")("highlights.sqlite");

async function exportHighlights() {
  const getBookListQuery =
    "SELECT DISTINCT content.ContentId, content.Title, content.Attribution AS Author " +
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
      const syncedTarget = querySyncedfromDB(title);
      if () {
        
      }
      let unSyncedTarget = queryUnsyncfromDB(title);

      // Use the results to determine status of the book
      var valid = false;
      const unSyncFound = (unSyncedTarget.results.length === 1);
      if (unSyncFound) {
        valid = true;
      } else if (syncedTarget) {
        onsole.log(`${title} synced. Skip Update Notes`);
      } else {
        console.log(`${title} unexisted. Try add Entry for it`);
        valid = addEntryByTitle(title);
      }
      if (valid != true && syncedTarget == false) {
        console.log(`Try Get Again after wait 2 second`);
        await sleep(2000);
        //Check Notion database for the book
        let unSyncedTarget = queryUnsyncfromDB(title);
        const unSyncAdded = (unSyncedTarget.results.length === 1);
        if (unSyncAdded){
          valid = true;
        }
      }
      valid = false;


      if (valid) {
        const pageId = response.results[0].id;
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

async function queryUnsyncfromDB(bookTitle) {
  let hasOnly = false;
  try {
    // Create a new entry in the Notion database
    const response = await notion.databases.query({
        database_id: NOTION_DATABASE_ID,
        filter: {
          and: [
            { property: "Title", text: { contains: bookTitle } },
            { property: "Exported", checkbox: { equals: false } },
          ],
        },
    });
    if (response.results.length === 1) {
      console.log(`Unsynced ${bookTitle} only one found.`);
      hasOnly = true;
    } else if (response.results.length > 1) {
      console.log(`Unsynced ${bookTitle} matched multiple items.`);
    } else {
      console.log(`Unsynced ${bookTitle} unexisted.`);
    }
    return response;
  } catch (error) {
    console.error('Error query[queryUnsyncfromDB]:', error.message);
  }
}

async function querySyncedfromDB(bookTitle) {
  let hasOnly = false;
  try {
    // Create a new entry in the Notion database
    const response = await notion.databases.query({
        database_id: NOTION_DATABASE_ID,
        filter: {
          and: [
            { property: "Title", text: { contains: bookTitle } },
            { property: "Exported", checkbox: { equals: true } },
          ],
        },
    });
    if (response.results.length === 1) {
      console.log(`Synced ${bookTitle} only one found.`);
      hasOnly = true;
    } else if (response.results.length > 1) {
      console.log(`Synced ${bookTitle} matched multiple items.`);
    } else {
      console.log(`Synced ${bookTitle} unexisted.`);
    }
    return hasOnly;
  } catch (error) {
    console.error('Error query [querySyncedfromDB]:', error.message);
  }
}

function sleep(ms) {
  return new Promise(resolve => {
    setTimeout(resolve, ms);
  });
}

exportHighlights();
