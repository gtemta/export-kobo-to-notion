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
  const getHighlightsQuery =
    "SELECT Bookmark.Text FROM Bookmark INNER JOIN content ON Bookmark.VolumeID = content.ContentID " +
    "WHERE content.ContentID = ? " +
    "ORDER BY content.DateCreated DESC";
  const bookList = db.prepare(getBookListQuery).all();

  for (const book of bookList) {
    try {
      console.log(`Get ${book.Title} from DB`)
      // Removes subtitles from book title
      const title = await getTitleWithoutSubtitle(book.Title);
      const { isTargetSynced, syncedTarget } = await checkBookSyncStatus(title);

      if (!isTargetSynced) {
        console.log(`${title} unexisted. Try adding entry for it`);
        const valid = await addEntryByTitle(title);

        if (!valid) {
          console.log(`Try getting again after waiting for 2 seconds`);
          await sleep(2000);
        }
        const { isTargetValid, unSyncedTarget } = await getUnSyncTarget(title);
        if (isTargetValid) {
          const pageId = unSyncedTarget.results[0].id;
          const highlightsList = db
            .prepare(getHighlightsQuery)
            .all(book.ContentID);
          
          await syncBookHighlights(pageId, highlightsList);
          await updateBookLRTime(pageId, book);
        } else {
          console.log(`Invalid sync Target skip update highlight`);
        }
      }

      if (isTargetSynced) {
        // Logic to update LastRead date...
        await updateBookLRTime(syncedTarget.results[0].id, book);
      }
    } catch (error) {
      console.log(`Error with ${book.Title}: `, error);
    }
  }
}

async function syncBookHighlights(pageId, highlightsList) {
  console.log(`Start Sync Highlights for pageId: ${pageId}`);
  const blocks = [];

  blocks.push({
    object: "block",
    type: "heading_1",
    heading_1: {
      text: [{ type: "text", text: { content: "Highlights" } }],
    },
  });

  for (const highlight of highlightsList) {
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
      await appendBlocksToPage(pageId, blocks);
      blocks.length = 0;
      console.log(`Clear Block to ${blocks.length}`);
    }
  }

  await appendBlocksToPage(pageId, blocks);

  await notion.pages.update({
    page_id: pageId,
    properties: { Exported: { checkbox: true } },
  });
}

async function appendBlocksToPage(pageId, blocks) {
  await notion.blocks.children.append({
    block_id: pageId,
    children: blocks,
  });
}

async function getTitleWithoutSubtitle(title) {
  if (title.indexOf(":") !== -1) {
    return title.substring(0, title.indexOf(":"));
  }
  return title;
}

async function checkBookSyncStatus(title) {
  const syncedTarget = await notion.databases.query({
    database_id: NOTION_DATABASE_ID,
    filter: {
      and: [
        { property: "Title", text: { contains: title } },
        { property: "Exported", checkbox: { equals: true } },
      ],
    },
  });
  return {
    isTargetSynced: syncedTarget.results?.length === 1,
    syncedTarget,
  };
}

async function getUnSyncTarget(title) {
  const unSyncedTarget = await notion.databases.query({
    database_id: NOTION_DATABASE_ID,
    filter: {
      and: [
        { property: "Title", text: { contains: title } },
        { property: "Exported", checkbox: { equals: false } },
      ],
    },
  });
  const isTargetValid = unSyncedTarget && unSyncedTarget.results
                           && unSyncedTarget.results.length > 0;
  return {
    isTargetValid,
    unSyncedTarget,
  };
}



async function updateBookLRTime(pageId, book) {
  await notion.pages.update({
    page_id: pageId,
    properties: {
      LastReadDate: {
        date: {
          start: book.DateLastRead,
        },
      },
    },
  });
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
