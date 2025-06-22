## Task

Create a robust novel reminder telegram bot using python-telegram-bot framework. It works by checking the novel's page at webnovel at a certain interval (configurable). The user can tell the bot which novel he wants to keep track of by simply sending the novel's url page

## Web Details

### URL

#### Novel's homepage

There are 2 url forms:
- title and id
https://www.webnovel.com/book/awakening-the-only-sss-rank-class!-now-even-dragons-obey-me_32382246008650205
- just id
https://www.webnovel.com/book/32382246008650205

There might be params or subdir after that, but ignore it. The id will be used as the main identifier for database and link constructor

#### Chapter list url

The chapter list is located at /catalog path. For example, https://www.webnovel.com/book/32382246008650205.

## Scrapping Method

Use httpx library (currently v1.7.0 as of April 2025) for scrapping the novel's page.
All fetch will go through our dedicated proxy as described in cors instruction.

## Userscript sample

Here is a fully working example of a userscript that's able to extract the full chapter list and last chapter metadata. Use that as a reference for the bot.

```js
// ==UserScript==
// @name         WebNovel Metadata Exporter
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Extracts novel and chapter metadata from a WebNovel catalog page into a JSON file.
// @author       Invictus
// @match        https://www.webnovel.com/book/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    /**
     * Creates and styles the download button.
     * @returns {HTMLButtonElement} The created button element.
     */
    function createDownloadButton() {
        const button = document.createElement('button');
        button.textContent = 'Export Metadata (JSON)';
        // Style the button to be visible and accessible
        Object.assign(button.style, {
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            zIndex: '9999',
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontSize: '16px',
            boxShadow: '0 2px 5px rgba(0,0,0,0.2)'
        });

        button.addEventListener('mouseover', () => button.style.backgroundColor = '#0056b3');
        button.addEventListener('mouseout', () => button.style.backgroundColor = '#007bff');

        return button;
    }

    /**
     * Parses the webpage to extract novel and chapter metadata.
     * @returns {object} An object containing all the extracted metadata.
     */
    function extractMetadata() {
        // Extract basic novel information
        const novelTitle = document.querySelector('h1.auto_height')?.textContent.trim() || 'Untitled';
        const author = document.querySelector('address .c_primary')?.textContent.trim() || 'Unknown Author';
        const coverUrl = document.querySelector('div._sd img')?.src || '';

        // Extract latest chapter information
        const latestChapterContainer = document.querySelector('.det-con-intro');
        const latestChapterAnchor = latestChapterContainer?.querySelector('a.lst-chapter');
        const latestChapter = {
            title: latestChapterAnchor?.textContent.trim() || 'Unknown',
            url: latestChapterAnchor?.href || '',
            published: latestChapterContainer?.querySelector('small.c_s')?.textContent.trim() || 'Unknown'
        };

        const volumes = [];
        // Iterate over each volume container
        document.querySelectorAll('.volume-item').forEach(volumeElement => {
            const volumeTitle = volumeElement.querySelector('h4')?.textContent.trim() || 'Untitled Volume';
            const chapters = [];

            // Iterate over each chapter list item within the volume
            volumeElement.querySelectorAll('ol.content-list > li').forEach(chapterElement => {
                const anchor = chapterElement.querySelector('a');
                if (!anchor) return; // Skip if no anchor tag is found

                const chapterNumber = parseInt(anchor.querySelector('._num')?.textContent.trim(), 10) || null;
                const title = anchor.querySelector('strong')?.textContent.trim() || 'Untitled Chapter';
                const url = anchor.href;
                const published = anchor.querySelector('small')?.textContent.trim() || 'Unknown Date';
                const isLocked = !!anchor.querySelector('svg._icon use[xlink\\:href="#i-lock"]');

                chapters.push({
                    chapterNumber,
                    title,
                    url,
                    published,
                    isLocked
                });
            });

            volumes.push({
                volumeTitle,
                chapters
            });
        });

        return {
            novelTitle,
            author,
            coverUrl,
            latestChapter,
            volumes
        };
    }

    /**
     * Triggers the download of the provided data as a JSON file.
     * @param {object} data - The data object to be downloaded.
     */
    function downloadJson(data) {
        const jsonString = JSON.stringify(data, null, 4);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        // Sanitize title for use in filename
        const fileName = (data.novelTitle || 'novel-metadata').replace(/[^a-z0-9]/gi, '_').toLowerCase();
        a.download = `${fileName}.json`;

        document.body.appendChild(a);
        a.click();

        // Cleanup
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Initializes the script by adding the button and its click handler.
     */
    function init() {
        const downloadButton = createDownloadButton();
        downloadButton.addEventListener('click', () => {
            console.log('Exporting metadata...');
            try {
                const metadata = extractMetadata();
                if (metadata.volumes.length === 0 || metadata.volumes.every(v => v.chapters.length === 0)) {
                   console.error("No chapters found to export.");
                   // A more user-friendly notification could be implemented here
                   return;
                }
                downloadJson(metadata);
                console.log('Metadata exported successfully.');
            } catch (error) {
                console.error('Failed to export metadata:', error);
            }
        });

        document.body.appendChild(downloadButton);
    }

    // Run the script
    init();

})();
```

## Features

Aside from the main feature of novel reminder and novel regisration, there should be a check update command that list the latest update on all novels he subscribed to, sorted by last updated time.

## Flexibility

You can create commands and features as you see fit. The goal is creating a production-ready telegram bot that ensures best User Experience (UX).
